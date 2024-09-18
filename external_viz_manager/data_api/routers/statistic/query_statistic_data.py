import os
import time
import django
from fastapi import status
from datetime import datetime
from typing import Callable
from typing import Optional
from fastapi import Depends
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute
from pydantic import BaseModel

django.setup()
from django.core.exceptions import ObjectDoesNotExist
from database.models import PlantInfo, StatisticCategory, StatisticSubCategory, StatisticsVar, VizStatistics
from database.models import StatisticCategoryLocalization, StatisticSubCategoryLocalization, Language

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler
    
router = APIRouter(
    prefix="/api/v1",
    tags=["Statistic"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)

class StatsRequest(BaseModel):
    plant_id:Optional[str] = None
    domain:Optional[str] = None
    language:Optional[str] = 'de'


description = """
    API Description for the get_stats Endpoint:

    Endpoint: /statistic
    Method: GET
    Tags: Statistic

    This API endpoint retrieves statistics related to a specific plant based on the plant_id or domain provided in the request, 
    with support for localized language content. It returns structured information about the plant and its associated statistical categories, 
    subcategories, and variable names, optionally localized into the requested language.
    Request Parameters:
    StatsRequest (Query Parameters):

        plant_id: (Optional) The unique identifier for the plant. Used to filter statistics by plant.
        domain: (Optional) The domain of the plant. Used to filter statistics by domain.
        language: (Optional, default: 'de') The language code to return the localized names of categories and subcategories. Default is German ('de').

    At least one of plant_id or domain must be provided.
    Response Structure:

        language: The name of the requested language (e.g., 'German').
        plant_name: The name of the plant.
        plant_domain: The domain of the plant.
        plant_id: The unique ID of the plant.
        plant_location: The location of the plant.
        data: A dictionary containing the categories and subcategories of statistics related to the plant. Each category contains:
            name: The localized name of the category.
            items: The subcategories within the category, where each subcategory contains:
                name: The localized name of the subcategory.
                url: A URL for accessing more detailed information about the subcategory.
                description: A localized description of the subcategory.
                var_names: A dictionary of variable names and values relevant to the subcategory.

    Error Handling:

        400 Bad Request: If neither plant_id nor domain are provided.

            {
                "error": {
                    "status_code": "bad request",
                    "description": "neither domain or plant_id are provided",
                    "detail": "at least one of domain or plant_id has to be given"
                }
            }

        404 Not Found: If the provided domain, plant_id, or language does not exist.

            {
                "error": {
                    "status_code": "not found",
                    "status_description": "domain or plant id not found",
                    "detail": "please provide a valid domain or plant id"
                }
            }

        500 Internal Server Error: If an unexpected server error occurs.

            {
                "error": {
                    "status_code": "server-error",
                    "status_description": "Internal Server Error",
                    "detail": "Error details"
                }
            }


"""


@router.api_route(
    "/statistic", methods=["GET"], tags=["Statistic"], description=description,
)
def get_stats(response: Response, request: StatsRequest = Depends()):
    results = {}
    try:
        plant_info = None
        if not request.domain and not request.plant_id:
            results["error"] = {
                "status_code": "bad request",
                "description": "neither domain or plant_id are provided",
                "detail": "at least one of domain or plant_id has to be given"
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
        
        if request.domain:
            if not PlantInfo.objects.filter(domain=request.domain).exists():
                results["error"] = {
                    "status_code": "not found",
                    "status_description": f"domain {request.domain} not found",
                    "detail": f"please provide a valid domain",
                }
            
                response.status_code = status.HTTP_404_NOT_FOUND
                return results
            
            plant_info = PlantInfo.objects.get(domain=request.domain)
            
        if request.plant_id and not plant_info:
            if not PlantInfo.objects.filter(plant_id=request.plant_id):
                results["error"] = {
                    "status_code": "not found",
                    "status_description": f"plant id {request.plant_id} not found",
                    "detail": f"please provide a valid plant id",
                }
            
                response.status_code = status.HTTP_404_NOT_FOUND
                return results
            
            plant_info = PlantInfo.objects.get(plant_id=request.plant_id)
        
        
        if not Language.objects.filter(code=request.language).exists():
            request["error"] = {
                "status_code": "not found",
                "status_description": f"language {request.language} not found",
                "deatil": f"language {request.language} not found",
            }
        
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        statistics = VizStatistics.objects.filter(plant=plant_info)
        language = Language.objects.get(code=request.language)
        
        data = {}
        for stat in statistics:
            category = stat.sub_category.category
            category_loc = StatisticCategoryLocalization.objects.get(category=category, language=language)
            sub_categories_loc = StatisticSubCategoryLocalization.objects.get(sub_category=stat.sub_category, language=language)
            
            if category.category_id not in data:
                data[category.category_id] = {
                    "name": category_loc.category_name,
                    "items": {},
                }
            
            var_names = StatisticsVar.objects.filter(sub_category=stat.sub_category)
            if not stat.sub_category.sub_category_id in data[category.category_id]['items']:
                data[category.category_id]["items"][stat.sub_category.sub_category_id] = {
                    "name": sub_categories_loc.sub_category_name,
                    "api_url": sub_categories_loc.url,
                    "description": sub_categories_loc.description,
                    "var_names": {
                        var.variable_key: var.variable_value for var in var_names
                    },
                    "urls": []

                }
  
            data[category.category_id]["items"][stat.sub_category.sub_category_id]['urls'].append(
                {
                    stat.url_name: {
                        "name": stat.url_name,
                        "url": stat.url
                    }
                }
            )
        
        results = {
            "language": language.name,
            "plant_name": plant_info.plant_name,
            "plant_domain": plant_info.domain,
            "plant_id": plant_info.plant_id,
            "plant_location": plant_info.plant_location,
            "data": data,           
        }
       
        results['status_code'] = "ok"
        results["detail"] = "data retrieved successfully"
        results["status_description"] = "OK"
        
    except ObjectDoesNotExist as e:
        results['error'] = {
            'status_code': "non-matching-query",
            'status_description': f'Matching query was not found',
            'detail': f"matching query does not exist. {e}"
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results
