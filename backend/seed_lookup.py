import csv
import os
import sqlalchemy as sa
from app import app, db
from models import Med_Lookup

def seed_medicines(csv_path):                        
    with app.app_context():
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            count = 0
            skipped = 0

            for row in reader:
                brand    = row.get('Brand Name', '').strip()
                generic  = row.get('Generic Name', '').strip()
                strength = row.get('Dosage Strength', '').strip()
                form     = row.get('Dosage Form', '').strip()
                category = row.get('Pharmacologic Category', '').strip()

                # check duplicates using a fresh query, no pending session objects
                exists = db.session.execute(
                    sa.select(Med_Lookup.lookup_id).where(
                        Med_Lookup.brand_name == brand,
                        Med_Lookup.generic_name == generic,
                        Med_Lookup.dosage_strength == strength
                    )
                ).scalar_one_or_none()

                if exists:
                    skipped += 1
                    continue

                db.session.add(Med_Lookup(
                    brand_name=brand or None,
                    generic_name=generic or None,
                    dosage_strength=strength or None,
                    dosage_form=form or None,
                    category=category or None
                ))
                count += 1

                # commit every 100 rows so session never gets too large
                if count % 100 == 0:
                    db.session.commit()
                    print(f"  {count} seeded so far...")

            db.session.commit()
            print(f"✅ Seeded {count} medicines, skipped {skipped} duplicates") 

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'all_drugproducts.csv')
    seed_medicines(csv_path)