from django import template
register = template.Library()

@register.filter
def calories_metric_illustrates(calories):
    if calories[0] == -1 and calories[1] == -1:
        return "Không giới hạn Calories"
    if calories[0] == -1:
        return "Dưới " + str(calories[1])
    if calories[1] == -1:
        return "Trên " + str(calories[0])
    return "Từ " + str(calories[0]) + " đến " + str(calories[1])
    