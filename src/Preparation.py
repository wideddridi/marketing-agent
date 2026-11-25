import pandas as pd
from sklearn.model_selection import train_test_split


def nettoyer(df):
    """Applique les décisions de nettoyage de l'exploration. Garde la colonne duration."""
    # Supprimer les doublons et renuméroter les lignes sans changer leur ordre
    df = df.drop_duplicates().reset_index(drop=True)
    # Cible en 0/1
    df["y_num"] = (df["y"] == "yes").astype(int)
    # Déjà contacté : au moins un contact avant cette campagne
    df["deja_contacte"] = (df["previous"] > 0).astype(int)
    # Nombre de jours depuis le dernier contact, -1 quand pdays vaut 999 (inconnu)
    df["pdays_jours"] = df["pdays"].where(df["pdays"] != 999, -1)
    df = df.drop(columns=["pdays"])
    # Regrouper les modalités trop rares
    df["default"] = df["default"].replace({"yes": "no"})
    df["education"] = df["education"].replace({"illiterate": "basic.4y"})
    # Version plafonnée à 20 pour la régression logistique
    df["campaign_plafonnee"] = df["campaign"].clip(upper=20)
    return df


def split_chronologique(df, prop_train=0.70, prop_val=0.15):
    """Découpe df (trié par date) en train / validation / test, sans mélange."""
    train, reste = train_test_split(df, train_size=prop_train, shuffle=False)
    val, test = train_test_split(reste, train_size=prop_val / (1 - prop_train), shuffle=False)
    return train.copy(), val.copy(), test.copy()


def split_aleatoire(df, cible="y_num", prop_train=0.70, prop_val=0.15, seed=42):
    """Découpe df au hasard, en gardant la même proportion de yes dans chaque jeu."""
    train, reste = train_test_split(df, train_size=prop_train,
                                    random_state=seed, stratify=df[cible])
    val, test = train_test_split(reste, train_size=prop_val / (1 - prop_train),
                                 random_state=seed, stratify=reste[cible])
    return train.copy(), val.copy(), test.copy()


def colonnes_entree(df, avec_duration=False):
    """Liste des colonnes utilisées comme variables d'entrée du modèle."""
    exclues = ["y", "y_num"]
    if not avec_duration:
        exclues.append("duration")
    return [c for c in df.columns if c not in exclues]
