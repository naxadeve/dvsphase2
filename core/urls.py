from django.urls import path, include
from core import views

urlpatterns = [
    path('partner/', views.PartnerView.as_view({'get': 'list'}), name='partner'),
    path('marker-category/', views.MarkerCategoryApi.as_view({'get': 'list'}), name='marker-category'),
    path('marker-value/', views.MarkerValueApi.as_view({'get': 'list'}), name='marker-value'),
    path('district/', views.DistrictApi.as_view({'get': 'list'}), name='district'),
    path('province/', views.ProvinceApi.as_view({'get': 'list'}), name='province'),
    path('municipality/', views.GapaNapaApi.as_view({'get': 'list'}), name='municipality'),
    path('fivew/', views.Fivew.as_view({'get': 'list'}), name='fivew'),
    path('fivew-district/', views.FiveWDistrict.as_view({'get': 'list'}), name='fivew-district'),
    path('fivew-province/', views.FiveWProvince.as_view({'get': 'list'}), name='fivew-province'),
    path('fivew-municipality/', views.FiveWMunicipality.as_view({'get': 'list'}), name='fivew-municipality'),
    path('contract-sum/', views.ContractSum.as_view({'get': 'list'}), name='contract-sum'),
    path('indicator-list/', views.IndicatorApi.as_view({'get': 'list'}), name='indicator-list'),
    path('municipality-indicator/', views.IndicatorData.as_view({'get': 'list'}), name='municipality-indicator'),
    path('sector/', views.SectorApi.as_view({'get': 'list'}), name='sector'),
    path('output/', views.OutputApi.as_view({'get': 'list'}), name='output'),
    path('sub-sector/', views.SubsectorApi.as_view({'get': 'list'}), name='sub-sector'),
    path('program/', views.ProgramTestApi.as_view({'get': 'list'}), name='program'),
    path('component/', views.ProjectApi.as_view({'get': 'list'}), name='component'),
    path('travel-time/', views.TravelTimeApi.as_view({'get': 'list'}), name='travel-time'),
    path('notification/', views.NotifyApi.as_view({'get': 'list'}), name='notification'),
    path('map-layer/', views.GisApi.as_view({'get': 'list'}), name='map-layer'),
    path('district-indicator/', views.DistrictIndicator.as_view({'get': 'list'}),
         name="district-indicator"),
    path('province-indicator/', views.ProvinceIndicator.as_view({'get': 'list'}),
         name="province-indicator"),
    path('summary/', views.SummaryData.as_view({'get': 'list'}), name='summary'),
    path('summary-nepal/', views.NepalSummaryApi.as_view({'get': 'list'}), name='summary-nepal'),
    path('sankey-program/', views.ProgramSankey.as_view({'get': 'list'}), name='sankey-program'),
    path('sankey-region/', views.RegionSankey.as_view({'get': 'list'}), name='region-region'),
    path('covid-fields/', views.CovidChoice.as_view({'get': 'list'}), name='covid-fields'),
    path('popup/', views.Popup.as_view({'get': 'list'}), name='popup'),
    path('feedbackform', views.Feedback.as_view({'post': 'create'}), name='feedbackfrom'),
    path('profile', views.RegionalProfile.as_view({'get': 'list'}), name='profile'),
    path('regional-sector-graph', views.RegionalSectorGraph.as_view({'get': 'list'}), name='sector-profile'),
    path('programprofile', views.ProgramProfile.as_view({'get': 'list'}), name='programprofile'),
    path('regionaldendrogram', views.RegionalDendrogram.as_view({'get': 'list'}), name='dendrogram'),
    path('programupperdendrogram', views.ProgramUpperDendrogram.as_view({'get': 'list'}),
         name='programupperdendrogram'),
    path('programlowerdendrogram', views.ProgramLowerDendrogram.as_view({'get': 'list'}),
         name='programlowerdendrogram'),
    path('faq/', views.FAQView.as_view({'get': 'list'}), name='faq'),
    path('national-statistic/', views.NationalStatisticView.as_view({'get': 'list'}), name='national-statistic'),
    path('terms-condition/', views.TermsAndConditionView.as_view({'get': 'list'}), name='terms-condition'),
    path('manual/', views.ManualViewSet.as_view({'get': 'list'}), name='manual'),

]
