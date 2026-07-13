from django.db import migrations


def seed_menu(apps, schema_editor):
    Menu = apps.get_model('restaurant', 'Menu')
    items = [
        ('Greek salad', 12.00, 'Fresh vegetables, feta cheese, olives.'),
        ('Bruschetta', 7.00, 'Grilled bread, tomato, garlic, basil.'),
        ('Grilled fish', 20.00, 'Catch of the day, chargrilled with lemon.'),
        ('Pasta', 15.00, 'Homemade pasta with a rich tomato sauce.'),
        ('Lemon dessert', 5.00, 'Our famous house specialty.'),
    ]
    for name, price, description in items:
        Menu.objects.get_or_create(
            name=name,
            defaults={'price': price, 'menu_item_description': description, 'inventory': 50},
        )


def remove_menu(apps, schema_editor):
    Menu = apps.get_model('restaurant', 'Menu')
    Menu.objects.filter(name__in=[
        'Greek salad', 'Bruschetta', 'Grilled fish', 'Pasta', 'Lemon dessert',
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_menu, remove_menu),
    ]
