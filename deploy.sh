#!/bin/bash

# Mise à jour du système
echo "Mise à jour des paquets..."
sudo apt update && sudo apt upgrade -y

# Installation des dépendances Docker et Nginx
echo "Installation de Docker, Docker Compose et Nginx..."
sudo apt install -y docker.io docker-compose nginx

# Activation de Docker et Nginx
echo "Activation de Docker et Nginx..."
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable nginx
sudo systemctl start nginx

# Définition des variables de nom de domaine
DOMAIN1="docker.canard.cc"
DOMAIN2="docker-db.canard.cc"
PORT1=8080
PORT2=8090

# Configuration de Nginx pour le premier domaine
echo "Configuration de Nginx pour $DOMAIN1..."
sudo tee /etc/nginx/sites-available/$DOMAIN1 > /dev/null <<EOL
server {
    listen 80;
    server_name $DOMAIN1;

    location / {
        proxy_pass http://localhost:$PORT1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Configuration de Nginx pour le deuxième domaine
echo "Configuration de Nginx pour $DOMAIN2..."
sudo tee /etc/nginx/sites-available/$DOMAIN2 > /dev/null <<EOL
server {
    listen 80;
    server_name $DOMAIN2;

    location / {
        proxy_pass http://localhost:$PORT2;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

sudo ln -s /etc/nginx/sites-available/$DOMAIN1 /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/$DOMAIN2 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Installation de Certbot pour SSL
echo "Installation de Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Obtention et installation des certificats SSL
echo "Obtention et installation des certificats SSL pour $DOMAIN1 et $DOMAIN2..."
sudo certbot --nginx -d $DOMAIN1 --non-interactive --agree-tos -m mathisjung02@gmail.com
sudo certbot --nginx -d $DOMAIN2 --non-interactive --agree-tos -m mathisjung02@gmail.com

# Lancement de l'application avec Docker Compose
echo "Lancement de l'application avec Docker Compose..."
sudo docker-compose up -d --build

sudo systemctl reload nginx

echo "Déploiement terminé avec succès !"
