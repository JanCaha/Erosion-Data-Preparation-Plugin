class KA5Class:

    def __init__(self,
                 id, code, name,
                 group_lv1_id,
                 group_lv2_id,
                 FT, MT, GT,
                 FU, MU, GU,
                 FS, MS, GS):

        self.id = id
        self.code = code
        self.name = name
        self.group_lv1_id = group_lv1_id
        self.group_lv2_id = group_lv2_id
        self.FT = FT
        self.MT = MT
        self.GT = GT
        self.FU = FU
        self.MU = MU
        self.GU = GU
        self.FS = FS
        self.MS = MS
        self.GS = GS

    def __repr__(self):
        return f"{self.name} - {self.code}"

    @classmethod
    def from_array(cls, data_array: list):

        if len(data_array) != 14:
            raise ValueError(F"KA5 category needs to be defined using 14 elements. "
                             F"Only {len(data_array)} are present.")

        return KA5Class(data_array[0],
                        data_array[1],
                        data_array[2],
                        data_array[3],
                        data_array[4],
                        data_array[5],
                        data_array[6],
                        data_array[7],
                        data_array[8],
                        data_array[9],
                        data_array[10],
                        data_array[11],
                        data_array[12],
                        data_array[13])

    def RMSE(self, other):

        MSE = 0

        MSE += pow(self.FT - other.FT, 2)
        MSE += pow(self.MT - other.MT, 2)
        MSE += pow(self.GT - other.GT, 2)
        MSE += pow(self.FU - other.FU, 2)
        MSE += pow(self.MU - other.MU, 2)
        MSE += pow(self.GU - other.GU, 2)
        MSE += pow(self.FT - other.FT, 2)
        MSE += pow(self.FS - other.FS, 2)
        MSE += pow(self.MS - other.MS, 2)
        MSE += pow(self.GS - other.GS, 2)

        return pow(MSE/9, 0.5)
