# Contexte Commercial & Cas d'Utilisation : Graphe de Connaissances Sémantiques Adventure Works

Ce document présente la valeur stratégique du projet Graph & Mining et détaille des cas d'utilisation commerciale spécifiques pour les algorithmes de graphe mis en œuvre.

---

## 🏢 Situation Commerciale : Refonte Stratégique

**Contexte :**
Adventure Works est un fabricant et distributeur mondial de vélos qui vend ses produits via un vaste réseau de revendeurs (boutiques de détail) et emploie une équipe répartie de représentants commerciaux.

**Le Problème :**
L'entreprise dispose d'une quantité massive de données transactionnelles (tables SQL) mais manque de vision *structurelle*. Elle sait *combien* elle a vendu, mais elle peine à répondre à des questions relationnelles :
*   "Pourquoi un revendeur à Seattle achète-t-il des combinaisons spécifiques de cadres et de casques ?"
*   "Quels produits stimulent la vente d'autres produits ?"
*   "Nos secteurs de vente sont-ils réellement alignés avec la façon dont nos équipes collaborent ?"

**La Solution :**
Ce projet intègre les données transactionnelles brutes dans un **Graphe de Connaissances Sémantiques Neo4j**. En modélisant les relations (ex: `COMMONLY_SOLD_BY_SAME_RESELLER`, `WORKS_WITH`), l'entreprise peut dépasser la simple agrégation et commencer à utiliser la **Graph Data Science (GDS)** pour découvrir des modèles cachés dans sa chaîne d'approvisionnement et son réseau de vente.

---

## 💡 Cas d'Utilisation Basés sur les Graphes

Les cas d'utilisation suivants exploitent les algorithmes et projections spécifiques mis en œuvre dans le projet.

### 1. Optimisation des Stocks et des Offres Groupées (Bundles)
*   **Algorithme :** **Détection de Communauté Louvain Pondérée** sur le **Graphe de Produits**.
    *   *Relation :* [`COMMONLY_SOLD_BY_SAME_RESELLER`](scripts/import_neo4j.py:128)
    *   *Poids :* Nombre de revendeurs stockant les deux articles.
*   **Application Commerciale :**
    *   **Création de Bundles :** L'algorithme identifie des grappes naturelles de produits (ex: regrouper des cadres spécifiques avec des porte-bidons et des pneus correspondants). Le marketing peut les packager sous forme de "Kits de démarrage pour la route".
    *   **Placement des Stocks :** Si un entrepôt stocke un produit principal, il devrait également stocker les accessoires associés identifiés dans sa communauté pour minimiser les fractionnements d'expédition et les coûts logistiques.

### 2. Analyse de Criticité de la Chaîne d'Approvisionnement
*   **Algorithme :** **PageRank Pondéré** sur le **Graphe de Produits**.
*   **Application Commerciale :**
    *   **Atténuation des Risques :** Identifie les "Produits Ancres" (nœuds à forte centralité comme le "HL Road Frame"). Ces articles sont les pivots structurels du réseau de vente.
    *   **Gestion des Priorités :** Les opérations doivent prioriser la chaîne d'approvisionnement pour ces articles. Une rupture de stock d'un Produit Ancre risque de briser la chaîne de vente de tous les accessoires périphériques qui lui sont connectés.

### 3. Réalignement des Secteurs de Vente
*   **Algorithme :** **Détection de Communauté Louvain** & **PageRank** sur le **Réseau de Vendeurs**.
    *   *Relation :* [`WORKS_WITH`](scripts/import_neo4j.py:121) (basé sur les régions partagées).
*   **Application Commerciale :**
    *   **Structuration d'Équipe :** Révèle les grappes de collaboration organiques. Si un vendeur est isolé de sa grappe assignée, cela peut indiquer un mauvais alignement sectoriel ou un besoin de mentorat.
    *   **Identification des Leaders :** PageRank identifie les influenceurs clés au sein de la force de vente qui peuvent diriger des initiatives de formation ou piloter de nouvelles stratégies de vente.

### 4. Substitution Intelligente de Produits & Recommandation
*   **Algorithme :** **Chemin le plus court de Dijkstra** sur le **Graphe de Connaissances**.
    *   *Chemin :* `(Produit A) -> (Sous-catégorie) -> (Catégorie) -> (Sous-catégorie) -> (Produit B)`
*   **Application Commerciale :**
    *   **Gestion des Ruptures de Stock :** Si un modèle spécifique est en rupture, le graphe trouve le chemin le plus court vers un substitut fonctionnellement identique (ex : même modèle, couleur différente) via les nœuds de métadonnées partagés.
    *   **Vente Croisée (Cross-Selling) :** Découvre des connexions non évidentes entre des produits disparates (ex : connecter un "VTT" à un "Casque de route" spécifique via les hiérarchies de catégories partagées ou les tendances régionales).

### 5. Rationalisation des Références (SKU)
*   **Algorithme :** **Similarité de Nœud (Jaccard)** sur le **Graphe de Produits**.
*   **Application Commerciale :**
    *   **Nettoyage du Catalogue :** Identifie les produits ayant un score de similarité de 1.0 (indiquant qu'ils sont vendus exactement au même ensemble de revendeurs).
    *   **Consolidation :** L'entreprise peut consolider ces références ou simplifier le suivi pour les variantes que le marché traite comme fonctionnellement identiques, réduisant ainsi les coûts administratifs et de stockage.
