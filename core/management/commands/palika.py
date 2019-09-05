from django.core.management.base import BaseCommand
import pandas as pd
from core.models import Province, District, GapaNapa


class Command(BaseCommand):
    help = 'load province data from province.xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']

        df = pd.read_csv(path)
        upper_range = len(df)

        print("Wait Data is being Loaded")

        try:
            # for row in range(0, upper_range):
                # GapaNapa.objects.create(
                #         province=Province.objects.get(province_name=int(df['province'][row])),
                #         district=District.objects.get(district_name=str((df['district'][row]).capitalize().strip())),
                #         name=(df['paulika_name'][row]).strip(),
                #         gn_type=df['gn_type'][row],
                #         cbs_code=df['lu_cbs_code'][row],
                #         hlcit_code=df['hlcit_id'][row],
                #         p_code=df['admin2pcode'][row],
                #
                #     )
                # print((df['district'][row]).capitalize())
                # a = District.objects.get(district_name=str((df['district'][row]).capitalize().strip()))
                # print(a)
            palika = [
                GapaNapa(
                    province=Province.objects.get(province_name=int(df['province'][row])),
                    district=District.objects.get(district_name=str((df['district'][row]).capitalize().strip())),
                    name=(df['paulika_name'][row]).capitalize().strip(),
                    gn_type=(df['gn_type'][row]).capitalize().strip(),
                    cbs_code=df['lu_cbs_code'][row],
                    hlcit_code=df['hlcit_id'][row],
                    p_code=df['admin2pcode'][row],

                ) for row in range(0, upper_range)
            ]

            palika_data = GapaNapa.objects.bulk_create(palika)
            print(palika_data)
            if palika_data:
                self.stdout.write('Successfully loaded Palika data ..')


        except Exception as e:
            print(e)
