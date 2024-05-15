import os
import docker
import shutil
import tarfile
from pathlib import Path
from typing import List, Dict, Union
import platform

class DockerHelper:
    def __init__(self):
        """Initialize the Docker client and set default parameters."""
        self.client = None
        self.container = None
        self.is_docker_installed = self._is_docker_installed()
        self.is_docker_running = False
        self.image = "python:latest"  # Official Python Docker image
        self.container_name = "default_python_container"

        if self.is_docker_installed:
            try:
                # Explicitly configure the Docker client
                self.client = docker.DockerClient(base_url=self._get_docker_base_url())
                self.client.ping()  # Test Docker connection with a ping
                self.is_docker_running = True
            except (docker.errors.DockerException, docker.errors.APIError) as e:
                print(f"Error initializing Docker client: {e}")
                self.client = None
                self.is_docker_running = False

    def _get_docker_base_url(self) -> str:
        """Get the base URL for the Docker connection.

        Returns:
            str: Docker base URL (unix socket or tcp)
        """
        if platform.system() == "Windows":
            return "tcp://localhost:2375"
        elif platform.system() == "Darwin":
            return "unix:///var/run/docker.sock"
        else:
            return "unix:///var/run/docker.sock"

    def _is_docker_installed(self) -> bool:
        """Check if Docker is installed on the system.

        Returns:
            bool: True if Docker is installed, False otherwise.
        """
        docker_installed = shutil.which("docker") is not None

        if not docker_installed:
            system = platform.system()

            if system == "Windows":
                # Check for Docker Desktop or other Docker installations on Windows
                docker_installed = (
                    os.path.exists("C:\\Program Files\\Docker\\Docker") or
                    os.path.exists("C:\\Program Files (x86)\\Docker\\Docker")
                )
            elif system == "Darwin":
                # Check for Docker Desktop on macOS
                docker_installed = (
                    shutil.which("docker") is not None or
                    os.path.exists("/Applications/Docker.app")
                )

        return docker_installed

    def check_docker_status(self) -> str:
        """Check if Docker is installed and running.

        Returns:
            str: Docker status ("installed", "not installed", "running", or "not running").
        """
        if not self.is_docker_installed:
            return "not installed"

        if self.is_docker_running:
            return "running"

        return "not running"

    def container_exists(self, container_name):
        """
        Check if a container with the specified name exists.
        
        :param container_name: Name of the container to check.
        :return: True if the container exists, False otherwise.
        """
        # List all containers, filter by name
        containers = self.client.containers.list(all=True, filters={"name": container_name})
        return any(container.name == container_name for container in containers)
    
    def create_instance(self, name: str = None, network: str = None):
        """Create a new Docker instance.

        Args:
            name (str, optional): Name for the Docker container. Defaults to "default_python_container".
            network (str, optional): Name of the Docker network bridge. Defaults to None.
            
        Returns:
            docker.models.containers.Container: The created container.
        """
        if self.check_docker_status() != "running":
            raise RuntimeError("Docker is not installed or not running.")

        try:
            self.client.images.pull(self.image)
        except docker.errors.APIError as e:
            print(f"Error pulling Docker image {self.image}: {e}")
            raise RuntimeError("Unable to pull Docker image. Please verify your credentials and image name.")

        name = name or self.container_name

        container_params = {
            "image": self.image,
            "command": "tail -f /dev/null",  # Keep the container running
            "detach": True,
            "name": name
        }

        if network:
            container_params["network"] = network

        self.container = self.client.containers.run(**container_params)
        print(f"Docker container '{name}' started.")
        return self.container

    def build_dockerfile(self, dockerfile_path: str, tag: str = "custom_python_image") -> str:
        """Build a Docker image from a local Dockerfile.

        Args:
            dockerfile_path (str): Path to the Dockerfile.
            tag (str, optional): Tag for the built image. Defaults to "custom_python_image".

        Returns:
            str: Tag of the created Docker image.
        """
        if self.check_docker_status() != "running":
            raise RuntimeError("Docker is not installed or not running.")

        dockerfile_dir = str(Path(dockerfile_path).parent)
        try:
            self.client.images.build(path=dockerfile_dir, dockerfile=dockerfile_path, tag=tag)
            print(f"Docker image '{tag}' built successfully.")
            self.image = tag
            return tag
        except docker.errors.BuildError as e:
            print(f"Error building Docker image '{tag}': {e}")
            raise RuntimeError(f"Unable to build Docker image from '{dockerfile_path}'.")

    def run_dockerfile(self, dockerfile_path: str, tag: str = "custom_python_image", name: str = "custom_python_container", ports: Dict[str, Union[str, int]] = None, environment: Dict[str, str] = None, volumes: Dict[str, Dict[str, str]] = None):
        """Build and run a Docker container from a Dockerfile.

        Args:
            dockerfile_path (str): Path to the Dockerfile.
            tag (str, optional): Tag for the built image. Defaults to "custom_python_image".
            name (str, optional): Name for the Docker container. Defaults to "custom_python_container".
            ports (Dict[str, Union[str, int]], optional): Port mappings. Defaults to None.
            environment (Dict[str, str], optional): Environment variables to set. Defaults to None.
            volumes (Dict[str, Dict[str, str]], optional): Volume mappings. Defaults to None.

        Returns:
            docker.models.containers.Container: The created container.
        """
        # Build the Dockerfile if necessary
        self.build_dockerfile(dockerfile_path, tag=tag)

        if self.check_docker_status() != "running":
            raise RuntimeError("Docker is not installed or not running.")

        try:
            self.container = self.client.containers.run(
                image=tag,
                command="tail -f /dev/null",  # Keep the container running
                detach=True,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes
            )
            print(f"Docker container '{name}' started using the image '{tag}'.")
            return self.container
        except docker.errors.APIError as e:
            print(f"Error running Docker container '{name}': {e}")
            raise RuntimeError(f"Unable to run Docker container '{name}'.")

    def write_file(self, local_file_path: str, container_dir_path: str):
        """Write a local file to the Docker instance.

        Args:
            local_file_path (str): Local path to the file.
            container_dir_path (str): Directory path within the Docker container.
        """
        file_name = Path(local_file_path).name
        tar_path = Path(local_file_path).with_suffix('.tar')

        with tarfile.open(tar_path, 'w') as tar:
            tar.add(local_file_path, arcname=file_name)

        with open(tar_path, 'rb') as f:
            self.container.put_archive(container_dir_path, f.read())

        os.remove(tar_path)
        print(f"File '{local_file_path}' written to Docker container at '{container_dir_path}/{file_name}'.")

    def write_folder(self, folder_path: str, container_path: str):
        """Write a local folder to the Docker instance.

        Args:
            folder_path (str): Local path to the folder.
            container_path (str): Path within the Docker container.
        """
        tar_path = Path(folder_path).with_suffix('.tar')
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(folder_path, arcname=Path(folder_path).name)

        with open(tar_path, 'rb') as f:
            self.container.put_archive(container_path, f.read())

        os.remove(tar_path)
        print(f"Folder '{folder_path}' written to Docker container at '{container_path}'.")

    def execute_command(self, command: Union[str, List[str]]) -> str:
        """Execute a command within the Docker instance and capture output.

        Args:
            command (Union[str, List[str]]): Command(s) to execute.

        Returns:
            str: Captured output from the executed command.
        """
        exec_result = self.container.exec_run(command, stdout=True, stderr=True)
        return exec_result.output.decode()

    def retrieve_file(self, container_path: str, local_path: str):
        """Retrieve a file from the Docker instance to the local filesystem.

        Args:
            container_path (str): Path to the file within the Docker container.
            local_path (str): Local path to save the retrieved file.
        """
        stream, stat = self.container.get_archive(container_path)

        with tarfile.open(fileobj=stream, mode='r') as tar:
            extracted_file = tar.getnames()[0]  # Extract the first file (should be only one)
            tar.extract(extracted_file, Path(local_path).parent)

            # Move the extracted file to the final location
            Path(local_path).parent.joinpath(extracted_file).rename(local_path)

        print(f"File '{container_path}' retrieved from Docker container to '{local_path}'.")

    def retrieve_folder(self, container_path: str, local_path: str):
        """Retrieve a folder from the Docker instance to the local filesystem.

        Args:
            container_path (str): Path to the folder within the Docker container.
            local_path (str): Local path to save the retrieved folder.
        """
        tar_path = Path(local_path).with_suffix('.tar')

        stream, stat = self.container.get_archive(container_path)
        with open(tar_path, 'wb') as f:
            for chunk in stream:
                f.write(chunk)

        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(local_path)

        os.remove(tar_path)
        print(f"Folder '{container_path}' retrieved from Docker container to '{local_path}'.")

    def shutdown_and_remove_instance(self):
        """Shutdown and remove the Docker instance if it exists."""
        if self.container:
            name = self.container.name
            self.container.stop()
            self.container.remove()
            self.container = None
            print(f"Docker container '{name}' stopped and removed.")

# Example Usage
"""
if __name__ == "__main__":
    docker_helper = DockerHelper()

    # Check Docker status
    status = docker_helper.check_docker_status()
    print(f"Docker status: {status}")

    if status == "running":
        # Build and run a Docker container from a Dockerfile
        docker_helper.run_dockerfile(
            dockerfile_path="Dockerfile",
            tag="custom_python_image",
            name="custom_python_container",
            ports={"8000/tcp": 8000},
            environment={"MY_ENV_VAR": "my_value"},
            volumes={"/host_folder": {"bind": "/container_folder", "mode": "rw"}}
        )

        # Write a file to the Docker instance
        docker_helper.write_file("local_file.txt", "/root")

        # Write a folder to the Docker instance
        docker_helper.write_folder("local_folder", "/root")

        # Execute a command in the Docker instance and print the output
        output = docker_helper.execute_command("ls /root")
        print(f"Output of command: {output}")

        # Retrieve the file from the Docker instance to the local system
        docker_helper.retrieve_file("/root/local_file.txt", "retrieved_file.txt")

        # Retrieve the folder from the Docker instance to the local system
        docker_helper.retrieve_folder("/root/local_folder", "retrieved_folder")

        # Shutdown and remove the Docker instance
        docker_helper.shutdown_and_remove_instance()
"""