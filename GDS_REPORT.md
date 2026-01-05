# Rapport d'Analyse des requêtes Graph Data Science (GDS) - Adventure Works

Ce rapport présente les résultats des analyses GDS effectuées sur les deux modèles de graphes projetés : le réseau des commerciaux (**Salesperson Network**) et le réseau des produits (**Product Network**).

---

## 1. Recherche de Chemin (Path Finding)
**Algorithme utilisé :** Dijkstra Shortest Path (unweighted)

### Salesperson Network
*   **Objectif :** Trouver le chemin le plus court entre deux commerciaux basés sur leurs collaborations (travail dans la même région).
*   **Résultat :** Le chemin identifié montre comment deux employés sont connectés à travers une chaîne de collègues partageant des territoires.
*   **Discussion :** Dans un contexte d'entreprise, cela permet d'identifier des intermédiaires clés pour le partage de connaissances entre des régions éloignées. Si le chemin est court (poids 1), ils travaillent directement ensemble. S'il est plus long, ils partagent des connaissances via des pivots.

### Product Network
*   **Objectif :** Trouver la distance entre deux produits basés sur leur vente par les mêmes revendeurs.
*   **Résultat :** Identifie si deux produits sont souvent vendus ensemble par une chaîne de revendeurs.
*   **Discussion :** Une distance courte indique une forte corrélation de marché. Si deux produits n'ont aucun chemin, cela signifie qu'ils appartiennent à des segments de revendeurs totalement disjoints (ex: vélos haut de gamme vs accessoires basiques).

---

## 2. Détection de Communautés (Communities)
**Algorithme utilisé :** Louvain

### Salesperson Network
*   **Objectif :** Grouper les commerciaux en équipes naturelles.
*   **Résultat :** L'algorithme a identifié des clusters qui correspondent généralement aux groupes géographiques (Group/Country).
*   **Discussion :** Cela valide la structure organisationnelle. Des communautés mélangeant plusieurs régions pourraient indiquer des commerciaux "pivots" ou des régions très interconnectées économiquement (ex: Europe Centrale).

### Product Network
*   **Objectif :** Identifier des "paniers" de produits ou des catégories de marché.
*   **Résultat :** Formation de groupes de produits fréquemment vendus ensemble par les mêmes revendeurs.
*   **Discussion :** On observe souvent que les produits d'une même `Subcategory` ou `Category` se retrouvent dans la même communauté, ce qui démontre la spécialisation des revendeurs Adventure Works.

---

## 3. Mesures de Centralité (Centralities)
**Algorithme utilisé :** PageRank

### Salesperson Network
*   **Objectif :** Identifier les commerciaux les plus "influents" ou connectés.
*   **Résultat :** Les scores PageRank les plus élevés reviennent aux commerciaux travaillant dans les régions les plus peuplées ou partageant le plus de territoires.
*   **Discussion :** Ces individus sont les nœuds critiques du réseau de communication interne. Leur départ pourrait fragiliser la circulation de l'information entre les équipes régionales.

### Product Network
*   **Objectif :** Déterminer les produits "piliers" du catalogue.
*   **Résultat :** Les produits avec le PageRank le plus élevé sont ceux qui sont vendus par le plus grand nombre de revendeurs diversifiés.
*   **Discussion :** Ce sont les produits d'appel (souvent les modèles de vélos les plus populaires). Ils servent de ponts entre différents types de revendeurs.

---

## 4. Prédiction de Liens (Link Prediction / Similarity)
**Algorithme utilisé :** Node Similarity (Jaccard)

### Salesperson Network
*   **Objectif :** Prédire quels commerciaux pourraient collaborer à l'avenir.
*   **Résultat :** Identifie des paires de commerciaux qui ne travaillent pas encore ensemble mais qui ont un voisinage (collègues) très similaire.
*   **Discussion :** C'est un outil puissant pour les RH pour suggérer des transferts ou des partages de bonnes pratiques entre des personnes ayant des profils de territoire similaires.

### Product Network
*   **Objectif :** Recommander des associations de produits.
*   **Résultat :** Détecte des produits qui sont vendus par des profils de revendeurs quasi identiques.
*   **Discussion :** C'est la base d'un système de recommandation "Next Best Offer". Si un revendeur vend le produit A mais pas le produit B (très similaire), il y a une opportunité de vente croisée (cross-selling).
