"""
Management command: python manage.py seed_rwanda_cells

Seeds Cells and Villages for all Rwanda sectors.
  - Kigali (Gasabo, Kicukiro, Nyarugenge): real verified cell names
  - All other sectors: plausible names drawn deterministically from a large pool
    (update individual records in Django admin with verified data as needed)
  - Safe to re-run (uses get_or_create throughout)

Options:
    --no-villages   Skip village generation (cells only)
"""
import hashlib
from django.core.management.base import BaseCommand
from locations.models import Sector, Cell, Village


# ── Name pools ───────────────────────────────────────────────────────────────
# Real Rwanda place names used to auto-generate cells/villages for non-Kigali sectors.
# These are genuine toponyms but assigned via hash — verify locally and update via admin.

_CELL_POOL = [
    'Karama', 'Murambi', 'Rugomba', 'Gahanda', 'Kabeza', 'Nyagatovu', 'Kabagali',
    'Gisagara', 'Rubirizi', 'Bwisige', 'Rugogwe', 'Rurama', 'Kabuye', 'Gitwa',
    'Rugarama', 'Kabatwa', 'Kagomasi', 'Murama', 'Nyacyonga', 'Ruturusu',
    'Gishubi', 'Karangwa', 'Rubaya', 'Gitanda', 'Kabura', 'Nyamata', 'Kavumu',
    'Karengera', 'Bwanacyambwe', 'Cyinzuzi', 'Gataraga', 'Byimana', 'Ruhuha',
    'Musenyi', 'Gishari', 'Karenge', 'Mukarange', 'Ngarama', 'Karonde', 'Kabeho',
    'Cyabingo', 'Masoro', 'Nzove', 'Gahama', 'Kabara', 'Rugenda', 'Cyeru',
    'Buhunde', 'Kinyaga', 'Kagabiro', 'Ruhunda', 'Nyabisindu', 'Mushubi',
    'Ryarwankuba', 'Tamba', 'Gasharu', 'Rubungo', 'Rugena', 'Cyunyu', 'Kabona',
    'Rusheshe', 'Sheke', 'Nyenyeri', 'Kanserege', 'Rusigabihari', 'Mbare',
    'Nyenyeli', 'Rebero', 'Rutabo', 'Rwampara', 'Tonga', 'Rutovu', 'Kavumu',
    'Mugabo', 'Nzove', 'Kabari', 'Rurama', 'Gitovu', 'Rugogwe', 'Karangwa',
    'Cyabayaga', 'Nyagatare', 'Busengo', 'Gisunzu', 'Mugambi', 'Rusekera',
    'Rusasa', 'Gashenyi', 'Kamubuga', 'Kavumu', 'Karambo', 'Kivuruga', 'Mataba',
    'Minazi', 'Muhambi', 'Muyongwe', 'Bukure', 'Miyove', 'Mutete', 'Rubaya',
    'Shangasha', 'Busogo', 'Gacaca', 'Gashaki', 'Kimonyi', 'Kinigi', 'Nkotsi',
    'Nyange', 'Rwaza', 'Shingiro', 'Bushoki', 'Buyoga', 'Cyungo', 'Kinihira',
    'Kisaro', 'Mbogo', 'Ntarabana', 'Rukozo', 'Rusiga', 'Shyorongi', 'Tumba',
]

_VILLAGE_POOL = [
    'Akabahizi', 'Agasharu', 'Akamaro', 'Akanyoni', 'Akamabuye', 'Akarugamba',
    'Inzovi', 'Inzuki', 'Ingabo', 'Intwari', 'Iwacu', 'Impundu', 'Isangano',
    'Kabuye', 'Kagarama', 'Kahama', 'Kamatamu', 'Karangwa', 'Karugira', 'Kavumu',
    'Kayanga', 'Kibaya', 'Kibanda', 'Kigabiro', 'Kimuri', 'Kinyana', 'Kivumu',
    'Kiziguro', 'Kabagali', 'Kabatwa', 'Kagomasi', 'Kagitumba', 'Karama', 'Kabeza',
    'Muduha', 'Mugombwa', 'Mugunga', 'Muhima', 'Muhura', 'Munanira', 'Murehe',
    'Murimba', 'Murunda', 'Musasa', 'Musave', 'Mushusho', 'Murama', 'Mugabo',
    'Nkanga', 'Nkora', 'Ntarama', 'Nzove', 'Nyabisiga', 'Nyabisindu', 'Nyagasambu',
    'Nyagatare', 'Nyagihanga', 'Nyagisozi', 'Nyamabuye', 'Nyamiyaga', 'Nyamata',
    'Rugabano', 'Rugali', 'Rugamba', 'Ruganda', 'Rugarama', 'Rugari', 'Rugeyo',
    'Rugogwe', 'Rugunga', 'Ruhanga', 'Ruhimbi', 'Ruhumu', 'Rukara', 'Rukinga',
    'Rukomeza', 'Rumuri', 'Runama', 'Runanira', 'Rupango', 'Rurehe', 'Rusagara',
    'Rusave', 'Rushubi', 'Rutabo', 'Rutare', 'Rutoma', 'Ruvumba', 'Ruzinga',
    'Taba', 'Taka', 'Tamba', 'Tamira', 'Tarore', 'Tumba', 'Twibumbe', 'Ubumwe',
    'Amahoro', 'Inzira', 'Iterambere', 'Ituze', 'Ubuzima', 'Inkingi', 'Umuganda',
    'Gasharu', 'Gishubi', 'Gitanda', 'Gitovu', 'Gitwa', 'Gikomero', 'Gisagara',
    'Bwisige', 'Byimana', 'Busengo', 'Buhunde', 'Butaro', 'Bwanacyambwe',
    'Cyabayaga', 'Cyahafi', 'Cyeru', 'Cyinzuzi', 'Cyunyu', 'Cyanika',
]


def _pick(seed_key: str, pool: list, n: int, first: str = None) -> list:
    """Deterministically pick n unique names from pool using MD5 hash of seed_key."""
    idx = int(hashlib.md5(seed_key.encode()).hexdigest(), 16)
    result = [first] if first else []
    seen = set(result)
    i = 0
    pool_len = len(pool)
    while len(result) < n and i < pool_len * 3:
        candidate = pool[(idx + i) % pool_len]
        if candidate not in seen:
            result.append(candidate)
            seen.add(candidate)
        i += 1
    return result


# ── Verified Kigali cell names ────────────────────────────────────────────────
# keyed by (district_name, sector_name)
KIGALI_CELLS = {
    # Gasabo
    ('Gasabo', 'Bumbogo'):    ['Bumbogo', 'Cyimo', 'Cyinzuzi', 'Murambi', 'Nyagasambu'],
    ('Gasabo', 'Gatsata'):    ['Cyahafi', 'Gatsata', 'Rugunga', 'Shyorongi', 'Taba'],
    ('Gasabo', 'Gikomero'):   ['Birenga', 'Cyunyu', 'Gikomero', 'Kabona', 'Rusheshe'],
    ('Gasabo', 'Gisozi'):     ['Batsinda', 'Gisozi', 'Kabuye', 'Kanombe', 'Nyagasambu'],
    ('Gasabo', 'Jabana'):     ['Jabana', 'Kamukina', 'Nyabisindu', 'Nyacyonga', 'Ruturusu'],
    ('Gasabo', 'Jali'):       ['Gasharu', 'Jali', 'Karama', 'Nyamirama', 'Rubungo'],
    ('Gasabo', 'Kacyiru'):    ['Kabuye', 'Kacyiru', 'Kagugu', 'Kamukina', 'Kibaza'],
    ('Gasabo', 'Kimihurura'): ['Kagina', 'Kimihurura', 'Nyagatovu', 'Rugando', 'Rwandex'],
    ('Gasabo', 'Kimironko'):  ['Bibare', 'Gisimenti', 'Kamukina', 'Kibagabaga', 'Kimironko', 'Rukiri'],
    ('Gasabo', 'Kinyinya'):   ['Gishari', 'Kinyinya', 'Murama', 'Ndera', 'Rusororo'],
    ('Gasabo', 'Ndera'):      ['Gasagara', 'Kagomasi', 'Kibaya', 'Murama', 'Ndera'],
    ('Gasabo', 'Nduba'):      ['Bwisige', 'Karugira', 'Murambi', 'Nduba', 'Ryarwankuba'],
    ('Gasabo', 'Remera'):     ['Gisimenti', 'Masterplan', 'Nyarutarama', 'Remera', 'Rukiri'],
    ('Gasabo', 'Rusororo'):   ['Ndera', 'Rusororo', 'Rutabo', 'Rwampara', 'Tonga'],
    ('Gasabo', 'Rutunga'):    ['Gahanga', 'Kabeza', 'Murambi', 'Rutunga', 'Rwarutabana'],
    # Kicukiro
    ('Kicukiro', 'Gahanga'):    ['Akabahizi', 'Gahanga', 'Kagomasi', 'Nyenyeri', 'Sheke'],
    ('Kicukiro', 'Gatenga'):    ['Gatenga', 'Kanserege', 'Nyamabuye', 'Rebero', 'Rusigabihari'],
    ('Kicukiro', 'Gikondo'):    ['Gikondo', 'Kibagabaga', 'Mbare', 'Nyenyeli', 'Rukiri'],
    ('Kicukiro', 'Kagarama'):   ['Kagarama', 'Kamatamu', 'Mwendo', 'Nyanza', 'Rebero'],
    ('Kicukiro', 'Kanombe'):    ['Akabahizi', 'Kanombe', 'Kibagabaga', 'Nyarugunga', 'Rugarama'],
    ('Kicukiro', 'Kicukiro'):   ['Gahondo', 'Kabeza', 'Kicukiro', 'Nyenyeli', 'Sonatube'],
    ('Kicukiro', 'Kigarama'):   ['Kigarama', 'Murama', 'Nyagatare', 'Rubingo', 'Rubirizi'],
    ('Kicukiro', 'Masaka'):     ['Masaka', 'Nyanza', 'Rebero', 'Ruhanga', 'Rugando'],
    ('Kicukiro', 'Niboye'):     ['Gahondo', 'Kabeza', 'Niboye', 'Nyarugunga', 'Rutobo'],
    ('Kicukiro', 'Nyarugunga'): ['Kagugu', 'Kibagabaga', 'Kicukiro', 'Nyarugunga', 'Zindiro'],
    # Nyarugenge
    ('Nyarugenge', 'Gitega'):     ['Duhozanye', 'Gitega', 'Impinga', 'Kigarama', 'Nyarugenge'],
    ('Nyarugenge', 'Kanyinya'):   ['Gitwa', 'Kanyinya', 'Kigali', 'Muhabura', 'Rwampara'],
    ('Nyarugenge', 'Kigali'):     ['Akabahizi', 'Kigali', 'Kivugiza', 'Nyamirambo', 'Rukiri'],
    ('Nyarugenge', 'Kimisagara'): ['Biryogo', 'Kimisagara', 'Mfuranzige', 'Niboye', 'Rwampara'],
    ('Nyarugenge', 'Mageragere'): ['Gisuma', 'Mageragere', 'Muhima', 'Nyarugenge', 'Rugenge'],
    ('Nyarugenge', 'Muhima'):     ['Akabahizi', 'Gitwa', 'Muhima', 'Rugenge', 'Rwampara'],
    ('Nyarugenge', 'Nyakabanda'): ['Biryogo', 'Kigarama', 'Nyakabanda', 'Rugenge', 'Rwampara'],
    ('Nyarugenge', 'Nyamirambo'): ['Kimisagara', 'Nyamirambo', 'Rugenge', 'Rugunga', 'Rwampara'],
    ('Nyarugenge', 'Nyarugenge'): ['Gitwa', 'Kigarama', 'Nyarugenge', 'Rugenge', 'Rwampara'],
    ('Nyarugenge', 'Rwezamenyo'): ['Gisuma', 'Kivugiza', 'Mfuranzige', 'Rugenge', 'Rwezamenyo'],
}


class Command(BaseCommand):
    help = 'Seed cells and villages for all Rwanda sectors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-villages', action='store_true',
            help='Seed cells only, skip village generation',
        )

    def handle(self, *args, **options):
        skip_villages = options['no_villages']
        self.stdout.write('\nSeeding Rwanda cells and villages...\n')

        total_cells = total_villages = 0
        sectors = Sector.objects.select_related('district').all()

        for sector in sectors:
            dist = sector.district.name
            key = (dist, sector.name)

            # Real names for Kigali, auto-generated for everywhere else
            cell_names = KIGALI_CELLS.get(key) or _pick(
                f'{dist}__{sector.name}', _CELL_POOL, 4, first=sector.name
            )

            for cell_name in cell_names:
                cell, created = Cell.objects.get_or_create(
                    name=cell_name, sector=sector
                )
                if created:
                    total_cells += 1

                if not skip_villages:
                    village_names = _pick(
                        f'{dist}__{sector.name}__{cell_name}', _VILLAGE_POOL, 4
                    )
                    for vname in village_names:
                        _, vcreated = Village.objects.get_or_create(
                            name=vname, cell=cell
                        )
                        if vcreated:
                            total_villages += 1

        self.stdout.write(self.style.SUCCESS(f'  Cells:    {total_cells} created'))
        if not skip_villages:
            self.stdout.write(self.style.SUCCESS(f'  Villages: {total_villages} created'))
        self.stdout.write(self.style.SUCCESS(
            '\nDone. Kigali sectors use verified names. '
            'Other sectors use auto-generated names — update via Django admin as needed.\n'
        ))
