import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel, ttest_1samp
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.api import anova_lm
import scipy
import json
from tqdm import tqdm
from pprint import pprint

FRANKLIN = 'FTCCMP1FRAN'
JEMISON = "FTCCMP1JEMI"
EDISON = "FTCCMP1EDIS"
OCHOA = "FTCCMP1OCHO"
ALLDIVS = [FRANKLIN, JEMISON, EDISON, OCHOA]
RANKS = "_rankings"

MATCHES = "_matches"
BLUEDRONE = "blue_Drone_Points"
REDDRONE = "red_Drone_Points"
DRONE = "Drone_Points"

def split_by_field_number(matches):
    field_1 = matches.iloc[::2] #  matches 1, 3, 5, etc. (rows 0, 2, 4, etc.)
    field_2 = matches.iloc[1::2] # matches 2, 4, 6, etc. (rows 1, 3, 5, etc.)
    return field_1, field_2

def split_by_red_blue(matches):
    red_col_names = []
    blue_col_names = []
    red_rename = {}
    blue_rename = {}
    for col_name in matches.columns:
        if not col_name.startswith('red'):
            blue_col_names.append(col_name)
            blue_rename[col_name] = col_name.replace('blue_', '')
        if not col_name.startswith('blue'):
            red_col_names.append(col_name)
            red_rename[col_name] = col_name.replace('red_', '')
    # print(red_rename, blue_rename)
    red = matches[red_col_names]
    red = red.rename(columns=red_rename)
    blue = matches[blue_col_names]
    blue = blue.rename(columns=blue_rename)
    return red, blue

def main():
    location_data_16 = []
    location_names_16 = []
    for div in ALLDIVS:
        rankings = pd.read_csv(div+RANKS+".csv")
        matches = pd.read_csv(div+MATCHES+".csv")

        print(div, 'mean:', (matches[REDDRONE].mean() + matches[BLUEDRONE].mean())/2)


        field_1, field_2 = split_by_field_number(matches)
        field_1_red, field_1_blue = split_by_red_blue(field_1)
        field_2_red, field_2_blue = split_by_red_blue(field_2)
        # print(div, 'field_1_red\n', field_1_red, '\n\n')
        # print(div, 'field_1_blue\n', field_1_blue, '\n\n')
        # print(div, 'field_2_red\n', field_2_red, '\n\n')
        # print(div, 'field_2_blue\n', field_2_blue, '\n\n')
        location_data_16.extend([field_1_red, field_1_blue, field_2_red, field_2_blue])
        location_names_16.extend([div[-4:] + ' field_1_red', div[-4:] + ' field_1_blue', div[-4:] + ' field_2_red', div[-4:] + ' field_2_blue'])

        for location_name in ['field_1_red', 'field_1_blue', 'field_2_red', 'field_2_blue']:

            location = eval(location_name)
            location['division'] = div
            location['location_name'] = location_name
            # print(div, location_name, '\taverage drone:', location[DRONE].mean(), ttest_1samp(location[DRONE], 0))
            # print(div, location_name, '\n', location, '\n', 'average drone:', location[DRONE].mean(), '\n')
            # quit()
            print(div, location_name, 'mean:', location[DRONE].mean(), 'var:', location[DRONE].var()**0.5)
        # continue
        print()

        # red_drone = matches[REDDRONE]
        # blue_drone = matches[BLUEDRONE]
        # test = ttest_rel(red_drone,blue_drone)
        # test = ttest_1samp(red_drone-blue_drone, popmean=0)
        # print(red_drone)
        # print(blue_drone)
        # print(red_drone - blue_drone)
        # print(np.mean(red_drone - blue_drone))
        # print(test)
    

    # print(location_data[0].info())
    # quit()
    # location_data = pd.concat(location_data_16)

    # print(len(location_data))

    # location_data["division"] = location_data["division"].astype("category")
    # location_data["location_name"] = location_data['location_name'].astype("category")
    # print(location_data.info())

    # print(location_data[DRONE])
    # # perform anova with factors divisions and location_name with drone points and final score.
    # # model = sm.GLM(location_data[["division","location_name"]], location_data[DRONE])
    # model = sm.ols(location_data[["division","location_name"]], location_data[DRONE])

    # #kruskal-wallis test

    # model.fit()
    # print(model.summary())


    # for values, group in location_data.groupby(["division","location_name"]):
    #     print(values, group[DRONE])

    # formula = DRONE + " ~ C(division) + C(location_name)"
    # lm = ols(formula, location_data).fit()
    # print(lm.summary())
    # print('@@@@@@@@@@@@@@@')
    # formula2 = DRONE + " ~ C(division) * C(location_name)"
    # lm2 = ols(formula2, location_data).fit()
    # print(lm2.summary())
    # print('@@@@@@@@@@@@@@@')

    # # infl = lm.get_influence()
    # # print(infl.summary_table())

    # table1 = anova_lm(lm, lm2)
    # print(table1)

    # interM_lm = ols("S ~ X + C(E)*C(M)", data=salary_table).fit()
    # print(interM_lm.summary())

    # table2 = anova_lm(lm, interM_lm)
    # print(table2)


    # variation due to: division, field number, 
    # 
    # rankings = pd.read_csv(RANK_DATAPATH)
    # matches = pd.read_csv(MATCH_DATAPATH)

    # print(matches.info())
    # print(rankings.info())

    # print(matches[REDDRONE])

    # print(matches[BLUEDRONE])
    # # red minus blue
    # rmb = matches[REDDRONE] - matches[BLUEDRONE]

    # test_results = ttest_1samp(rmb, popmean=0)
    # print(test_results)

    res = scipy.stats.tukey_hsd(*[x[DRONE] for x in location_data_16])
    print(res, '\n\n\n\n\n')
    # quit()

    confs = {} # {(1,2): 0.5, (3,4): 0.6}
    for i in tqdm(range(1, 100)):
        conf_level = i/100

        conf = res.confidence_interval(confidence_level=conf_level)
        for ((i, j), l) in np.ndenumerate(conf.low):
            # filter out self comparisons
            if i != j:
                h = conf.high[i,j]
                if (l < 0 and h < 0) or (l > 0 and h > 0):
                    # print('@@@', end='')
                    confs[(i,j)] = conf_level
                    # above.append((i,j))
                # print(f"({i} - {j}) {l:>6.3f} {h:>6.3f}")

        # print(conf_level, len(above), above)
    # pprint({k: v for k, v in sorted(confs.items(), key=lambda item: item[1])})
    print('confidence levels that each pair is significantly different')
    for k, v in sorted(confs.items(), key=lambda item: item[1]):
        print(v, k, location_names_16[k[0]], location_names_16[k[1]])

    print('\n')
    confs_each = {}
    for k, v in confs.items():
        for loc in k:
            if not loc in confs_each:
                confs_each[loc] = []
            confs_each[loc].append(v)
        # print(k)
        # confs_each[k]
    for k, v in confs_each.items():
        avg = 0
        if len(v) > 0:
            avg = sum(v)/len(v)
        confs_each[k] = avg
            
    print('confidence that each location is different that the average other location:')
    for k, v in sorted(confs_each.items(), key=lambda item: item[1]):
        # print(k, v, location_names_16[k])
        print(location_names_16[k], '\t', v)

    # for i, name in enumerate(location_names_16):
        # print(i, name)
        # results = []
        # for l1 in location_data_16:
        #     for l2 in location_data_16:
        #         test = ttest_1samp(l1[DRONE] - l2[DRONE], popmean=0).pvalue
        #         # print(('%.5f' % test).ljust(16), end='\t')
        #     # print()

if __name__ == "__main__":
    main()
