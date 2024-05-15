steps:
1) planner; break the input text into steps; sharing what kind of actions are available for each step (interactions folder descriptions).
2) process each step with an agent which as all the methods of the chosen interactions folder available as well as a general 'interactions' class (read content of file x, get sourcetree, etc)
3) give the tools of the assigned classification folder to the LLM, to interact with the contents as needed to achieve the task step currently being processed. 

```bash
m "crea una presentación"
```

```bash
m "crea una presentación sobre las últimas 10 propiedades publicadas en Las Condes en el sitio portalinmobiliario.com. Incluye ubicación, caracteristicas y precio."
```

```bash
m "crea un servidor fastapi en python que se inicie con docker"
```

```bash
m "agrega un endpoint llamado obtener_tickets, que se conecte con un servidor JIRA y extraiga todas las tareas que contengan el label 'expandir_qa', y las retorne como un array de objetos"
```

```bash
m "agrega un endpoint llamado leer_ticket, que acepte un ticket de JIRA, obtenga su descripción, labels y enlaces, y los retorne como un objeto."
```

```bash
m "agrega un endpoint llamado leer_ticket, que acepte un ticket de JIRA, obtenga su descripción, labels y enlaces, y los retorne como un objeto."
```

```bash
m "lee mi cv y hazme una version más profesional para la oferta en http://xx en cv2.docx"
```

Tarea más compleja, desde 0 a varios pasos:
```bash
m "crea un servidor fastapi en python que contenga un endpoint que permita leer los tickets de un servidor JIRA que contengan la etiqueta 'expandir_qa'. Luego que por cada ticket encontrado, extraiga los links de confluence que se encuentren en su descripción y los lea. Luego por cada confluence link, los analice, transforme las imagenes a diagramas mermaid y use el contenido como contexto para extraer lo siguiente:
1. nombres y cargos de los encargados de la historia
2. cree casos de uso para el area de QA y las agrupe según las personas a cargo cuyos cargos indicados son relacionados a los casos de uso respectivos.
3. para cada grupo del paso 2, cree un ticket en JIRA asociado a la persona a cargo, con los 'casos de uso' generados en la descripción.
"
```