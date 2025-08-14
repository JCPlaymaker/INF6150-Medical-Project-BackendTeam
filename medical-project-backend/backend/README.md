# INF6150
Afin de faciliter la mise en place de l'environnement de développement, deux options sont possible.
1. L'API sera toujours disponible sur un serveur hébergé afin de recevoir les requêtes HTTP de l'équipe de développement. 
Le domain du serveur est disponible dans le fichier `.env` partager sur discord. Ce fichier n'est pas diffuser sur
gitlab étant donné qu'il contient des données sensibles comme les accès à la base de donnés.
Tout les demandes nécessitant un appel à la base de données se feront par l'API et donc vous
n'aurez pas besoin avec cette méthode de vous connecter avec la base de données.
2. Si vous souhaiter mettre en place l'API et la base de données localement sur votre machine, le processus est facilité par la mise en place d'un fichier `compose.yml`. 
L'utilisation de la commande `docker compose` avec ce fichier crééra d'un container docker sur votre machine. 
L'un pour la base de données PostgreSQL et l'autre pour l'API. Les instructions pour la mise en place local avec docker vont suivre.

## Mise en place local du backend
Vous devez tout d'abord installer `docker compose` si ce n'est pas déja fait. Vous pouvez trouver les instructions au lien suivant :
[Overview of installing Docker Compose](https://docs.docker.com/compose/install/)
Une fois installer, vous pouvez exécuter la commande dans le répertoire du `compose.yml` afin de crééer les deux containers :
```sh
docker compose up --build -d
```
Cette commande lancera l'API et la base de données.
Elle exécutera aussi des commandes établies par le backend qui créerons les tables et insérons dans la base de données des données de test.
