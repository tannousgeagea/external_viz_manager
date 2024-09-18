from django.contrib import admin

# Register your models here.
from .models import PlantInfo
from .models import StatisticCategory, VizStatistics, StatisticsVar, StatisticSubCategory
from .models import Language, StatisticCategoryLocalization, StatisticSubCategoryLocalization

class StatisticsVarInline(admin.TabularInline):
    model = StatisticsVar
    extra = 0


@admin.register(PlantInfo)
class PlantInfoAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'plant_name', 'plant_location', 'domain', 'created_at')
    search_fields = ('plant_id', 'plant_name', 'plant_location')
    list_filter = ('plant_location', 'created_at')
    ordering = ('-created_at',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(StatisticCategory)
class StatisticCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'created_at')
    search_fields = ('category_id',)
    ordering = ('created_at',)
    
    class StatisticCategoryLocalizationInline(admin.TabularInline):
        model = StatisticCategoryLocalization
        extra = 1
        min_num = 1

    class StatisticSubCategoryInline(admin.TabularInline):
        model = StatisticSubCategory
        extra = 1
        min_num = 1


    inlines = [StatisticCategoryLocalizationInline, StatisticSubCategoryInline]

@admin.register(StatisticCategoryLocalization)
class StatisticCategoryLocalizationAdmin(admin.ModelAdmin):
    list_display = ('category', 'language', 'category_name', 'url')
    search_fields = ('category__category_id', 'category_name', 'language__name')
    list_filter = ('language',)
    ordering = ('category', 'language')


@admin.register(StatisticSubCategory)
class StatisticSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('sub_category_id', 'category', 'created_at')
    search_fields = ('sub_category_id', 'category__category_id')
    list_filter = ('category',)
    ordering = ('created_at',)
    
    class StatisticSubCategoryLocalizationInline(admin.TabularInline):
        model = StatisticSubCategoryLocalization
        extra = 1
        min_num = 1
        
    class VizStatisticsInline(admin.TabularInline):
        model = VizStatistics
        extra = 1
        min_num = 1
        
    class StatisticsVarInline(admin.TabularInline):
        model = StatisticsVar
        extra = 1
        min_num = 1
        
    inlines = [StatisticSubCategoryLocalizationInline, VizStatisticsInline, StatisticsVarInline]


@admin.register(StatisticSubCategoryLocalization)
class StatisticSubCategoryLocalizationAdmin(admin.ModelAdmin):
    list_display = ('sub_category', 'language', 'sub_category_name', 'description', 'url')
    search_fields = ('sub_category__sub_category_id', 'sub_category_name', 'language__name')
    list_filter = ('language',)
    ordering = ('sub_category', 'language')


@admin.register(VizStatistics)
class VizStatisticsAdmin(admin.ModelAdmin):
    list_display = ('plant', 'sub_category', 'url_name', 'url', 'created_at')
    search_fields = ('plant__plant_id', 'sub_category__sub_category_id', 'url_name')
    list_filter = ('plant', 'sub_category')
    ordering = ('created_at',)


@admin.register(StatisticsVar)
class StatisticsVarAdmin(admin.ModelAdmin):
    list_display = ('sub_category', 'variable_key', 'variable_value', 'created_at')
    search_fields = ('sub_category__sub_category_id', 'variable_key')
    list_filter = ('sub_category',)
    ordering = ('created_at',)

