from django.db import models

# Create your models here.
class PlantInfo(models.Model):
    plant_id = models.CharField(max_length=255, unique=True)
    plant_name = models.CharField(max_length=255)
    plant_location = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'plant_info'
        verbose_name_plural = 'Plant Information'
        unique_together = ('plant_name', 'plant_location')

    def __str__(self):
        return f"{self.plant_name} in {self.plant_location}"

class Language(models.Model):
    """
    Model to define and manage supported languages.
    """
    code = models.CharField(max_length=10, unique=True)  # ISO 639-1 language codes, e.g., 'en', 'fr'
    name = models.CharField(max_length=50)  # e.g., 'English', 'French'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return f"{self.name} ({self.code})"

class StatisticCategory(models.Model):
    category_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'statistic_category'
        verbose_name_plural = 'Statistic Categories'

    def __str__(self):
        return f"{self.category_id}"

class StatisticCategoryLocalization(models.Model):
    category = models.ForeignKey(StatisticCategory, on_delete=models.CASCADE, related_name='Localizations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)

    class Meta:
        db_table = 'statistic_category_Localization'
        unique_together = ('category', 'language')
        verbose_name_plural = 'Statistic Category Localizations'

    def __str__(self):
        return f"{self.category.category_id} - {self.language}"

class StatisticSubCategory(models.Model):
    sub_category_id = models.CharField(max_length=255)
    category = models.ForeignKey(StatisticCategory, on_delete=models.CASCADE, related_name='sub_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'statistic_sub_category'
        verbose_name_plural = 'Statistic Sub Categories'
        unique_together = ("sub_category_id", "category")

    def __str__(self):
        return f"{self.category}, {self.sub_category_id}"

class StatisticSubCategoryLocalization(models.Model):
    sub_category = models.ForeignKey(StatisticSubCategory, on_delete=models.CASCADE, related_name='Localizations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    sub_category_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)

    class Meta:
        db_table = 'statistic_sub_category_Localization'
        unique_together = ('sub_category', 'language')
        verbose_name_plural = 'Statistic Sub Category Localizations'

    def __str__(self):
        return f"{self.sub_category.sub_category_id} - {self.language}"

class VizStatistics(models.Model):
    plant = models.ForeignKey(PlantInfo, on_delete=models.CASCADE, related_name='visual_statistics')
    sub_category = models.ForeignKey(StatisticSubCategory, on_delete=models.CASCADE, related_name='visual_statistics')
    url_name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'visual_statistics'
        verbose_name_plural = 'Visual Statistics'

    def __str__(self):
        return f"{self.sub_category} - {self.url_name}"

class StatisticsVar(models.Model):
    sub_category = models.ForeignKey(StatisticSubCategory, on_delete=models.CASCADE, related_name='variables')
    variable_key = models.CharField(max_length=255)
    variable_value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "statistic_variables"
        verbose_name_plural = 'Statistic Variables'

    def __str__(self):
        return f"{self.sub_category.sub_category_id} - {self.variable_key}"
