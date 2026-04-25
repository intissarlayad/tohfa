"""
Script d'initialisation de la base de données TOHFA v2.
Lance une seule fois pour créer les tables et seeder les tissus.
"""
from app import app, db
from models import User, Fabric, Design, Selection


def reset_and_seed():
    with app.app_context():
        print("── Création des tables ──────────────────────")
        db.create_all()
        print("Tables créées.")

        # Nettoyage
        Selection.query.delete()
        Design.query.delete()
        Fabric.query.delete()
        User.query.delete()
        db.session.commit()
        print("Base nettoyée.")

        # ── Tissus ───────────────────────────────────────
        all_fabrics = [
            Fabric(name="Acier Brossé",       description="Un gris industriel noble avec un reflet métallique.",              image_url="/static/images/Acier Bross\u00e9.jpeg"),
            Fabric(name="Atlas Azur",          description="Le bleu profond des cieux de l'Atlas, texture soyeuse.",           image_url="/static/images/Atlas Azur.jpeg"),
            Fabric(name="Aube Rosée",          description="Une teinte délicate rappelant les premières lueurs du jour.",      image_url="/static/images/Aube Ros\u00e9e.jpeg"),
            Fabric(name="Baroque Sidéral",     description="Motifs complexes et sombres pour une élégance mystérieuse.",      image_url="/static/images/Baroque Sid\u00e9ral.jpeg"),
            Fabric(name="Beige Héritage",      description="Le classique intemporel, doux et polyvalent.",                    image_url="/static/images/Beige H\u00e9ritage.jpeg"),
            Fabric(name="Bleu Ardoise",        description="Un bleu gris sobre et professionnel.",                             image_url="/static/images/Bleu Ardoise.jpeg"),
            Fabric(name="Bleu Impérial",       description="Le prestige d'un bleu puissant et profond.",                      image_url="/static/images/Bleu Imp\u00e9rial.jpeg"),
            Fabric(name="Cachemerie de Soie",  description="Le mélange parfait entre chaleur et fluidité.",                   image_url="/static/images/Cachemerie de Soie.jpeg"),
            Fabric(name="Caramel Étoilé",      description="Une nuance chaude parsemée de reflets subtils.",                  image_url="/static/images/Caramel \u00c9toil\u00e9.jpeg"),
            Fabric(name="Choko Argenté",       description="Un brun riche rehaussé de fils d'argent.",                        image_url="/static/images/Choko Argent\u00e9.jpeg"),
            Fabric(name="Ciel Doré",           description="Le contraste magnifique entre le bleu clair et l'or.",           image_url="/static/images/Ciel Dor\u00e9.jpeg"),
            Fabric(name="Comète Grise",        description="Un gris chiné avec une brillance discrète.",                      image_url="/static/images/Com\u00e8te Grise.jpeg"),
            Fabric(name="Cristal Rosé",        description="Translucide et brillant, pour des créations féeriques.",          image_url="/static/images/Cristal Ros\u00e9.jpeg"),
            Fabric(name="Dune de Soie",        description="Une couleur sable texturée comme le désert au soleil.",           image_url="/static/images/Dune de Soie.jpeg"),
            Fabric(name="Émeraude Baroque",    description="Vert profond aux motifs royaux travaillés.",                      image_url="/static/images/Emeraude Baroque.jpeg"),
            Fabric(name="Galaxie Sombre",      description="Noir intense parsemé de points lumineux.",                        image_url="/static/images/Galaxie Sombre.jpeg"),
            Fabric(name="Jardin Suspendu",     description="Motifs floraux délicats sur fond fluide.",                        image_url="/static/images/Jardin Suspendu.jpeg"),
            Fabric(name="Liane de Minuit",     description="Un tissage sombre évoquant la nature nocturne.",                  image_url="/static/images/Liane de Minuit.jpeg"),
            Fabric(name="Majesté Marine",      description="Le bleu des grands océans, lourd et majestueux.",                 image_url="/static/images/Majest\u00e9 Marine.jpeg"),
            Fabric(name="Mousseline d'Or",     description="Légèreté absolue et reflets dorés prestigieux.",                  image_url="/static/images/Mousseline d'Or.jpeg"),
            Fabric(name="Nuage Poudré",        description="Une texture vaporeuse et un rose très pâle.",                    image_url="/static/images/Nuage Poudr\u00e9.jpeg"),
            Fabric(name="Palais de Perles",    description="Un blanc nacré d'une pureté exceptionnelle.",                    image_url="/static/images/Palais de Perles.jpeg"),
            Fabric(name="Patine Royale",       description="Un aspect noble vieilli par le temps.",                           image_url="/static/images/Patine Royale.jpeg"),
            Fabric(name="Pavé de Nacre",       description="Texture structurée avec des reflets irisés.",                    image_url="/static/images/Pav\u00e9 de Nacre.jpeg"),
            Fabric(name="Perle Dorée",         description="Le luxe d'une perle avec une aura d'or.",                        image_url="/static/images/Perle Dor\u00e9e.jpeg"),
            Fabric(name="Samae Doré",          description="Inspiré par le ciel radieux et l'éclat du soleil.",              image_url="/static/images/Samae Dor\u00e9.jpeg"),
            Fabric(name="Saphire Céleste",     description="L'éclat d'une pierre précieuse dans un tissu.",                  image_url="/static/images/Saphire C\u00e9leste.jpeg"),
            Fabric(name="Sillage d'Or",        description="Un tissage qui laisse une trace lumineuse derrière lui.",         image_url="/static/images/Sillage d'Or.jpeg"),
            Fabric(name="Soleil de Soie",      description="Capturer la chaleur de la lumière dans la soie.",                image_url="/static/images/Soleil de Soie.jpeg"),
            Fabric(name="Tosca Red",           description="Un rouge passionnel et théâtral.",                                image_url="/static/images/Tosca Red.jpeg"),
        ]
        db.session.add_all(all_fabrics)
        db.session.commit()
        print(f"{len(all_fabrics)} tissus insérés.")
        print("── Base initialisée avec succès ✨ ─────────")


if __name__ == '__main__':
    reset_and_seed()
