from scipy.integrate import odeint
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import plotly.express as px

rCt = 0.3
rOa = 0.32
KCOa = 7027
KCCt = 6874
qCt = 909280
qOa = 4321535
M = 10000
KT = 0.015
N0 = [1E8, 1E9]
xs = np.arange(0, 500, 0.5)


def plot_N(ct, oa):
    plt.plot(xs, ct, label='ct')
    plt.plot(xs, oa, label='oa')
    # plt.yscale("log")
    plt.legend()
    plt.show()


def plot_rel(ct, oa):
    plt.plot(xs, ct, label='ct')
    plt.plot(xs, oa, label='oa')
    # plt.yscale("log")
    plt.legend()
    plt.show()


def plot_R(R, T):
    plt.plot(xs, R, label='Citrate')
    plt.plot(xs, T, label='Thiamin')
    plt.yscale("log")
    plt.legend()
    plt.show()


def fixed_thiamin(y, t, c, a, D):
    R = y[0]
    T = y[1]
    Ct = y[2]
    Oa = y[3]
    dR = D * M - D * R - rCt * R / (R + KCCt) * \
        Ct/qCt - rOa * R / (R + KCOa) * Oa/qOa
    dCt = rCt * R / (KCCt + R) * Ct - D * Ct
    dOa = min(rOa * R / (KCOa + R), rOa * T / (T + KT)) * Oa - D * Oa
    #dOa = rOa * R / (KCOa + R)* rOa * T / (T + KT) * Oa - D * Oa
    if c is not None:
        dT = D * (c - T)
    if a is not None:
        dT = rCt * R / (R + KCCt) * Ct/qCt * a - D * \
            T - rOa * T / (T + KT) * Oa / 1E15
    return [dR, dT, dCt, dOa]


def constant_thiamine():
    colors = {'<i>O. anthropi</i>': '#e27e50',
              '<i>C. testosteroni</i>': '#8872cd'}
    cs = [1.5]
    dfs = []
    xs = range(400)
    for i, c in enumerate(cs):
        y0 = [M, 0, 0.9E9, 8E9]
        y = odeint(fixed_thiamin, y0, xs, args=(c, None, 0.04))
        df = pd.DataFrame(columns=['x', 'y', 'species', 'linegroup'])
        df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                                   2], '<i>C. testosteroni</i>', c, y[:, 1], y[:, 0]
        dfs.append(df)
        df = pd.DataFrame(columns=['x', 'y', 'species', 'linegroup'])
        df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                                   3], '<i>O. anthropi</i>', c, y[:, 1], y[:, 0]
        dfs.append(df)
        df = pd.DataFrame(columns=['x', 'y', 'species', 'linegroup'])
        df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                               3] + y[:, 2], 'total', None, y[:, 1], y[:, 0]
        dfs.append(df)
    out = pd.concat(dfs)
    fig = px.line(out, x='x', y='y',
                  color='species', log_y=True,height=400,width=500)
    for i, d in enumerate(fig['data'][:-1]):
        d['line']['color'] = colors[d['legendgroup']]
    fig.update_xaxes(title='Time [h]')
    fig.update_yaxes(title='CFUs/mL')
    
    # fig.show()
    return fig


def thiamine_cross_feeding(D,xs):
    colors = {'<i>O. anthropi</i>': '#e27e50',
              '<i>C. testosteroni</i>': '#8872cd'}
    dfs = []
    y0 = [M, 0, 0.9E9, 8E9]
    y = odeint(fixed_thiamin, y0, xs, args=(None, 5E-6, D))
    df = pd.DataFrame()
    df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                               2], '<i>C. testosteroni</i>', None, y[:, 1], y[:, 0]
    dfs.append(df)
    df = pd.DataFrame(columns=['x', 'y', 'species', 'linegroup'])
    df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                               3], '<i>O. anthropi</i>', None, y[:, 1], y[:, 0]
    dfs.append(df)
    df = pd.DataFrame(columns=['x', 'y', 'species', 'linegroup'])
    df['x'], df['y'], df['species'], df['linegroup'], df['T'], df['C'] = xs, y[:,
                                                                               3] + y[:, 2], 'total', None, y[:, 1], y[:, 0]
    dfs.append(df)
    out = pd.concat(dfs)
    fig = px.line(out, x='x', y='y',
                  color='species', log_y=True,height=400,width=500)
    for i, d in enumerate(fig['data'][:-1]):
        d['line']['color'] = colors[d['legendgroup']]
    fig.update_xaxes(title='Time [h]')
    fig.update_yaxes(title='CFUs/mL')

    fig_T = px.line(out[['x', 'T', 'linegroup']
                        ].drop_duplicates(), x='x', y='T', log_y=True)
    fig_C = px.line(out[['x', 'C', 'linegroup']
                        ].drop_duplicates(), x='x', y='C')
    return fig, fig_T, fig_C,y


f = pd.read_csv(join('data', 'plate_reader_resources', 'data.csv'))
