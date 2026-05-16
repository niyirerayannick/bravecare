"""
Management command: python manage.py seed_rwanda_locations

Seeds:
  - Common countries with phone codes
  - Rwanda: all 5 provinces, all 30 districts, all ~416 sectors
  - Cells and villages can be imported via CSV (too numerous to hardcode)

Safe to re-run — uses get_or_create throughout.
"""
from django.core.management.base import BaseCommand
from locations.models import Country, Province, District, Sector


COUNTRIES = [
    ('Rwanda',                  '+250', 'RW'),
    ('Uganda',                  '+256', 'UG'),
    ('Kenya',                   '+254', 'KE'),
    ('Tanzania',                '+255', 'TZ'),
    ('Burundi',                 '+257', 'BI'),
    ('Democratic Republic of Congo', '+243', 'CD'),
    ('Ethiopia',                '+251', 'ET'),
    ('South Sudan',             '+211', 'SS'),
    ('United States',           '+1',   'US'),
    ('United Kingdom',          '+44',  'GB'),
    ('France',                  '+33',  'FR'),
    ('Belgium',                 '+32',  'BE'),
    ('Netherlands',             '+31',  'NL'),
    ('Germany',                 '+49',  'DE'),
    ('Canada',                  '+1',   'CA'),
    ('South Africa',            '+27',  'ZA'),
    ('Nigeria',                 '+234', 'NG'),
    ('Ghana',                   '+233', 'GH'),
]

# Province -> District -> [Sectors]
RWANDA_DATA = {
    'City of Kigali': {
        'Gasabo': [
            'Bumbogo', 'Gatsata', 'Gikomero', 'Gisozi', 'Jabana', 'Jali',
            'Kacyiru', 'Kimihurura', 'Kimironko', 'Kinyinya', 'Ndera',
            'Nduba', 'Remera', 'Rusororo', 'Rutunga',
        ],
        'Kicukiro': [
            'Gahanga', 'Gatenga', 'Gikondo', 'Kagarama', 'Kanombe',
            'Kicukiro', 'Kigarama', 'Masaka', 'Niboye', 'Nyarugunga',
        ],
        'Nyarugenge': [
            'Gitega', 'Kanyinya', 'Kigali', 'Kimisagara', 'Mageragere',
            'Muhima', 'Nyakabanda', 'Nyamirambo', 'Nyarugenge', 'Rwezamenyo',
        ],
    },
    'Northern Province': {
        'Burera': [
            'Bungwe', 'Butaro', 'Cyanika', 'Cyeru', 'Gahunga', 'Gatebe',
            'Gitovu', 'Kagogo', 'Kinoni', 'Kinyababa', 'Kivuye', 'Nemba',
            'Rugarama', 'Rugendabari', 'Ruhunde', 'Rusarabuye', 'Rwerere',
        ],
        'Gakenke': [
            'Busengo', 'Coko', 'Cyabingo', 'Gakenke', 'Gashenyi', 'Janja',
            'Kamubuga', 'Karambo', 'Kivuruga', 'Mataba', 'Minazi', 'Muhondo',
            'Muyongwe', 'Muzo', 'Nemba', 'Ruli', 'Rusasa', 'Rushashi',
        ],
        'Gicumbi': [
            'Bukure', 'Bwisige', 'Byumba', 'Cyumba', 'Giti', 'Kaniga',
            'Manyagiro', 'Miyove', 'Mukarange', 'Muko', 'Mutete', 'Nyamiyaga',
            'Nyankenke', 'Rubaya', 'Rukomo', 'Rushaki', 'Rutare', 'Ruvune',
            'Rwamiko', 'Shangasha',
        ],
        'Musanze': [
            'Busogo', 'Cyuve', 'Gacaca', 'Gashaki', 'Gataraga', 'Kimonyi',
            'Kinigi', 'Muhoza', 'Muko', 'Musanze', 'Nkotsi', 'Nyange',
            'Remera', 'Rwaza', 'Shingiro',
        ],
        'Rulindo': [
            'Base', 'Burega', 'Bushoki', 'Buyoga', 'Cyinzuzi', 'Cyungo',
            'Kinihira', 'Kisaro', 'Masoro', 'Mbogo', 'Murambi', 'Ngoma',
            'Ntarabana', 'Rukozo', 'Rusiga', 'Shyorongi', 'Tumba',
        ],
    },
    'Southern Province': {
        'Gisagara': [
            'Gikonko', 'Gishubi', 'Kansi', 'Kibilizi', 'Kigembe', 'Mamba',
            'Muganza', 'Mugombwa', 'Mukingo', 'Muyira', 'Ndora', 'Nzangwa',
            'Nyanza', 'Save',
        ],
        'Huye': [
            'Gishamvu', 'Huye', 'Karama', 'Kigoma', 'Kinazi', 'Maraba',
            'Mbazi', 'Mukura', 'Ngoma', 'Ruhashya', 'Rusatira', 'Rwaniro',
            'Simbi', 'Tumba',
        ],
        'Kamonyi': [
            'Gacurabwenge', 'Karama', 'Kayenzi', 'Kayumbu', 'Mugina',
            'Musambira', 'Ngamba', 'Nyamiyaga', 'Nyarubaka', 'Rugarika',
            'Rukoma', 'Runda',
        ],
        'Muhanga': [
            'Cyeza', 'Kabacuzi', 'Kibangu', 'Kiyumba', 'Muhanga',
            'Mushishiro', 'Nyabinoni', 'Nyamabuye', 'Nyamiyaga', 'Rongi',
            'Rugendabari', 'Shyogwe',
        ],
        'Nyamagabe': [
            'Buruhukiro', 'Cyanika', 'Gasaka', 'Gatare', 'Kaduha', 'Kamegeli',
            'Kibumbwe', 'Kitabi', 'Mbazi', 'Mugano', 'Musange', 'Musebeya',
            'Mushubi', 'Nkomane', 'Tare', 'Uwinkingi',
        ],
        'Nyanza': [
            'Busasamana', 'Busoro', 'Cyabakamyi', 'Kibirizi', 'Kigoma',
            'Mukingo', 'Muyira', 'Ntyazo', 'Nyagisozi', 'Rwabicuma',
            'Rwanyamahembe',
        ],
        'Nyaruguru': [
            'Kibeho', 'Kivu', 'Mata', 'Muganza', 'Munini', 'Ngera', 'Ngoma',
            'Nyabimata', 'Nyagisozi', 'Ruheru', 'Ruramba', 'Rusenge',
            'Runyinya', 'Simbi',
        ],
        'Ruhango': [
            'Byimana', 'Kabagari', 'Kinazi', 'Kinihira', 'Mbuye',
            'Mwendo', 'Ntongwe', 'Ruhango',
        ],
    },
    'Eastern Province': {
        'Bugesera': [
            'Gashora', 'Juru', 'Kamabuye', 'Mareba', 'Mayange', 'Muganza',
            'Musenyi', 'Muyumbu', 'Mwogo', 'Ngeruka', 'Ntarama', 'Nyamata',
            'Nyarugenge', 'Rilima', 'Ruhuha', 'Rweru', 'Shyara',
        ],
        'Gatsibo': [
            'Gasange', 'Gatsibo', 'Gitoki', 'Kagitumba', 'Kabarore',
            'Kiramuruzi', 'Kiziguro', 'Muhura', 'Murambi', 'Ngarama',
            'Nyagihanga', 'Remera', 'Rugarama', 'Rwimbogo',
        ],
        'Kayonza': [
            'Gahini', 'Kabare', 'Kabarondo', 'Mukarange', 'Murama',
            'Murundi', 'Mwiri', 'Ndego', 'Nyamirama', 'Nyarubuye',
            'Ruramira', 'Rwinkwavu',
        ],
        'Kirehe': [
            'Gahara', 'Gatore', 'Kigarama', 'Kigina', 'Kirehe', 'Mahama',
            'Mpanga', 'Musaza', 'Mushikiri', 'Nasho', 'Nyamugari', 'Nyarubuye',
        ],
        'Ngoma': [
            'Gashanda', 'Jarama', 'Karembo', 'Kazo', 'Kibungo', 'Mugesera',
            'Murama', 'Mutenderi', 'Remera', 'Rukira', 'Rukumberi',
            'Rurenge', 'Sake', 'Zaza',
        ],
        'Nyagatare': [
            'Gatunda', 'Karama', 'Karangazi', 'Katabagemu', 'Matimba',
            'Mimuli', 'Mukama', 'Musheli', 'Nyagatare', 'Rukomo',
            'Rwempasha', 'Rwimiyaga', 'Tabagwe',
        ],
        'Rwamagana': [
            'Fumbwe', 'Gahengeri', 'Gishali', 'Karenge', 'Kigabiro',
            'Muhazi', 'Munyaga', 'Munyiginya', 'Musha', 'Muyumbu',
            'Nzige', 'Rubona',
        ],
    },
    'Western Province': {
        'Karongi': [
            'Bwishyura', 'Gashari', 'Gishyita', 'Gitesi', 'Mubuga',
            'Murambi', 'Murundi', 'Mutuntu', 'Rubengera', 'Rugabano',
            'Ruganda', 'Rwankuba', 'Twumba',
        ],
        'Ngororero': [
            'Bwira', 'Gatumba', 'Hindiro', 'Kabaya', 'Kageyo', 'Kavumu',
            'Matyazo', 'Muhanda', 'Muhororo', 'Ndaro', 'Ngororero',
            'Nyange', 'Sovu',
        ],
        'Nyabihu': [
            'Bigogwe', 'Jenda', 'Jomba', 'Kabatwa', 'Karago', 'Kintobo',
            'Mukamira', 'Muringa', 'Rambura', 'Rugera', 'Rurembo', 'Shingiro',
        ],
        'Nyamasheke': [
            'Bushekeri', 'Bushenge', 'Cyato', 'Gihombo', 'Kagano', 'Kanjongo',
            'Karambi', 'Karengera', 'Kirimbi', 'Macuba', 'Mahembe',
            'Nyabitekeri', 'Rangiro', 'Ruharambuga', 'Sainte-Emeraude', 'Yove',
        ],
        'Rubavu': [
            'Bugeshi', 'Busasamana', 'Cyanzarwe', 'Gisenyi', 'Kanama',
            'Kanzenze', 'Mudende', 'Nyamyumba', 'Nyundo', 'Rubavu', 'Rugerero',
        ],
        'Rutsiro': [
            'Boneza', 'Gihango', 'Kigeyo', 'Kivumu', 'Manihira', 'Mukura',
            'Murunda', 'Musasa', 'Mushonyi', 'Mushubati', 'Nyabirasi',
            'Ruhango', 'Rusebeya',
        ],
        'Rusizi': [
            'Bugarama', 'Butare', 'Bweyeye', 'Gashonga', 'Giheke',
            'Gihundwe', 'Gitambi', 'Kamembe', 'Muganza', 'Mururu', 'Nkanka',
            'Nkungu', 'Nyakabuye', 'Nyakarenzo', 'Nzahaha', 'Rwimbogo',
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed countries, and Rwanda provinces/districts/sectors'

    def handle(self, *args, **options):
        self.stdout.write('\nSeeding location data...\n')

        # ── Countries ──
        self.stdout.write('  Countries...')
        for name, phone_code, iso_code in COUNTRIES:
            Country.objects.get_or_create(
                iso_code=iso_code,
                defaults={'name': name, 'phone_code': phone_code},
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(COUNTRIES)} countries ready.'))

        # ── Rwanda admin structure ──
        rwanda, _ = Country.objects.get_or_create(
            iso_code='RW',
            defaults={'name': 'Rwanda', 'phone_code': '+250'},
        )

        total_provinces = total_districts = total_sectors = 0

        for province_name, districts in RWANDA_DATA.items():
            province, _ = Province.objects.get_or_create(
                name=province_name, country=rwanda
            )
            total_provinces += 1

            for district_name, sector_names in districts.items():
                district, _ = District.objects.get_or_create(
                    name=district_name, province=province
                )
                total_districts += 1

                for sector_name in sector_names:
                    Sector.objects.get_or_create(
                        name=sector_name, district=district
                    )
                    total_sectors += 1

        self.stdout.write(self.style.SUCCESS(
            f'  Rwanda: {total_provinces} provinces, {total_districts} districts, '
            f'{total_sectors} sectors seeded.'
        ))
        self.stdout.write(self.style.WARNING(
            '  Note: Cells and Villages must be imported via CSV — '
            'run: python manage.py import_location_csv <file>'
        ))
        self.stdout.write(self.style.SUCCESS('\nLocation seed complete.\n'))
