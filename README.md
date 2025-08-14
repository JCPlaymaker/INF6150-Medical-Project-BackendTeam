# Application Médicale

Développement d’une application médicale permettant aux utilisateurs du système de santé d'avoir un dossier médical centralisé, peu importe les médecins ou l'établissement qu'ils fréquentent. 

Le dossier médical d'un patient sera centralisé. 

À chaque fois qu'un patient visite un médecin, le médecin aura accès à l'ensemble du dossier du patient, incluant son historique de visites, les autres médecins traitant le patient, les diagnostics connus et ainsi de suite.

La problématique du système actuel réside dans le fait que Les données médicales sont dispersées entre différents médecins, ou plateformes. 

Ce qui rend difficile le suivi complet d'un patient, en cas de prise en charge multiple ou lors de changements de professionnels de santé. 

Cette fragmentation peut entraîner des erreurs médicales, des duplications d'examens ou des traitements incohérents. 

La décentralisation du système actuel entraine des difficultés de communication entre les différents professionnels de santé (médecins généralistes, spécialistes, hôpitaux, infirmières, etc.). 

Cela conduit à des délais dans le traitement, des erreurs de diagnostic, des parcours de soins inefficaces, ou des erreurs dans les dossiers des patients. 

Les mises à jour des dossiers des patients, la sauvegarde des données et le suivi des performances sont également plus simples à réaliser.

<img width="865" height="557" alt="image" src="https://github.com/user-attachments/assets/835fb05c-1cfc-4aa9-a176-0408c6558a49" />

<img width="865" height="336" alt="image" src="https://github.com/user-attachments/assets/0bfa29cb-35b0-4636-a1bf-927ea4f933ff" />

Les fonctionnalités du système

•	Le patient ne peut rien modifier dans son dossier, sauf ses coordonnées.
•	Chaque modification faite par un médecin est automatiquement sauvegardée au dossier, sans que le médecin n'ait explicitement à sauvegarder les modifications.
•	Un médecin peut, en tout temps, annuler les modifications qu'il a apporté à un dossier.
•	Plusieurs médecins peuvent apporter des modifications à un même dossier en même temps sans conflit de concurrence.
•	Chaque modification faite au dossier doit être archivée. En tout temps, un dossier complet doit pouvoir se reconstruire, tel qu'il était à cette époque, à partir d'une modification précise faite dans le passé. Un dossier peut être également reconstruite à une date donnée.
La carte d'assurance-maladie du patient deviendra la façon d'accéder au dossier du patient. La carte sera munie d'une puce électronique qui émettra un code lorsque présentée devant l'ordinateur d'un médecin. Avec ce code, le dossier du patient pourra être téléchargé afin d'être consulté par le médecin. La carte d'assurance-maladie peut aussi être présentée à un professionnel de la santé (non médecin) pour un accès en lecture seule du dossier
