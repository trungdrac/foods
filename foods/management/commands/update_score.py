from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg

from foods.models import Dish, Rating


class Command(BaseCommand):
    help = 'Update dish average score'

    def handle(self, *args, **options):
        dishes = Dish.objects.filter(is_public=True)
        if dishes:
            for d in dishes:
                ratings = Rating.objects.filter(dish=d)
                if ratings:
                    avg = ratings.aggregate(Avg('score'))
                    d.score = avg['score__avg']
                    d.save()
            self.stdout.write(self.style.SUCCESS('Update dish score successfully.'))
        else:
            raise CommandError('No public dish found.')
