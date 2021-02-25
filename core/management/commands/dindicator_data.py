from django.core.management.base import BaseCommand
import pandas as pd
from core.models import Indicator, IndicatorValue, GapaNapa, District
from django.core.exceptions import ObjectDoesNotExist


def gapanapa(code):
    try:
        obj = GapaNapa.objects.get(hlcit_code=str(code))
    except ObjectDoesNotExist:
        obj = None
    return obj

def district(code):
    try:
        obj = District.objects.get(hlcit_code=str(code))
    except ObjectDoesNotExist:
        obj = None
    return obj

class Command(BaseCommand):
    help = 'load province data from province.xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']

        df = pd.read_csv(path)
        upper_range = len(df)
        print("Wait Data is being Loaded")
        df_col_list = list(df.columns)
        category_name = ((path.split('/'))[-1]).replace('.csv', '')
        not_cols = ['District', 'district', 'Name of municipalities', 'Name of Municipalities', 'CBS_CODE',
                    'HLCIT_CODE', 'Province', 'province', 'Palika',
                    'palika', 'CBS_Code', 'District ', 'code', 'cbs code']
        try:
            for col in df_col_list:
                if not col in not_cols:
                    indicator_value = [
                        IndicatorValue(
                            indicator_id=Indicator.objects.get(indicator=col, category=category_name),
                            #gapanapa_id=gapanapa(df['HLCIT_CODE'][row]) if 'HLCIT_CODE' in df_col_list else None,
                            district_id=((gapanapa(df['HLCIT_CODE'][row])).district_id if gapanapa(
                                df['HLCIT_CODE'][row]) is not None else None) if 'HLCIT_CODE' in df_col_list else None,
                            value=df[col][row],

                        ) for row in range(0, upper_range)
                    ]
                    indicator_data = IndicatorValue.objects.bulk_create(indicator_value)

            if indicator_data:
                self.stdout.write('Successfully loaded Indicator Value  ..')
            # for row in range(0, upper_range):
            #     print(df['District_ID'][row])
            #     d = District.objects.get(code=df['District_ID'][row])
            #     print(d.name)



        except Exception as e:
            print(e)