import pandas as pd
import numpy as np

#class Bradesco:
def tabela_fm(fm):
    print('============================================================================   ')
    print('                                    FM                                         ')
    print('============================================================================ \n')
    iof=float(0.0238)
    cols_fm=['TIPO DO REGISTRO','NUMERO DA SUBFATURA','NUMERO DO CERTIFICADO','COMPLEMENTO DO CERTIFICADO',
    'NOME SEGURADO/DEPENDENTE','INDIC. SUBF. ANTER/ATUAL','DATA DE NASCIMENTO','CODIGO DO SEXO',
    'ESTADO CIVIL','COD. GRAU PARENT.DEP.','CODIGO DO PLANO','DATA INICIO VIGENCIA','TIPO DE LANÇAMENTO',
    'DATA DE LANCAMENTO','VALOR DO LANCAMENTO','PARTE DO SEGURADO','CODIGO DO LANCAMENTO','CARGO / OCUPACAO',
    'MATRICULA ESPECIAL']

    col_specification = [(0, 1), (1,5),(5,12),(12,14),(14,53),(52,53),(53,61),(61,62),(62,63),(63,64),(64,68),
                        (68,76),(76,78),(78,84),(84,99),(99,114),(114,116),(116,136),(136,148)]#,(148,181)]
    df_fm=pd.read_fwf(fm, colspecs=col_specification,skiprows=0,header=None)

    df_fm.columns=cols_fm

    df_fm_3=df_fm[df_fm['TIPO DO REGISTRO']=='3']

    #tratando colunas
    df_fm_3['DATA DE NASCIMENTO'] = [str(data_n).replace('.','')[0:2]+'/'+str(data_n).replace('.','')[2:4]+'/'+str(data_n).replace('.','')[4:8] for data_n in df_fm_3['DATA DE NASCIMENTO']]
    df_fm_3['DATA INICIO VIGENCIA'] = [str(data_n).replace('.','')[0:2]+'/'+str(data_n).replace('.','')[2:4]+'/'+str(data_n).replace('.','')[4:8] for data_n in df_fm_3['DATA INICIO VIGENCIA']]
    df_fm_3['VALOR DO LANCAMENTO'] = [float(int(valor)/100) for valor in df_fm_3['VALOR DO LANCAMENTO']]

    df_fm_3['CODIGO DO LANCAMENTO']=[int(str(cod)) for cod in df_fm_3['CODIGO DO LANCAMENTO']]
    df_fm_3.loc[df_fm_3['CODIGO DO LANCAMENTO']>=50,'N1']=int(-1)
    df_fm_3.loc[df_fm_3['CODIGO DO LANCAMENTO']<50,'N1']=int(+1)

    df_fm_3['VALOR DO LANCAMENTO']=df_fm_3['N1']*df_fm_3['VALOR DO LANCAMENTO']
    #separando valores de taxa
    df_fm_3_taxa=df_fm_3.loc[df_fm_3['NOME SEGURADO/DEPENDENTE']=='COB.REF. TAXA IMPLANTACAO']
    #separando colunas de taxa
    df_ac=df_fm_3_taxa[['NUMERO DA SUBFATURA','NOME SEGURADO/DEPENDENTE','TIPO DE LANÇAMENTO','VALOR DO LANCAMENTO']]
    #separando inclusão mês
    df_fm_3_sep=df_fm_3[['NUMERO DA SUBFATURA','COD. GRAU PARENT.DEP.','COMPLEMENTO DO CERTIFICADO','NOME SEGURADO/DEPENDENTE','TIPO DE LANÇAMENTO','VALOR DO LANCAMENTO']].loc[df_fm_3['TIPO DE LANÇAMENTO']=='IM']
    #contando quantas pessoas foram incluidas no mês
    piv_im=pd.pivot_table(df_fm_3_sep,values='TIPO DE LANÇAMENTO',index='NUMERO DA SUBFATURA',aggfunc=len)
    #juntando contagem com valores de taxa
    piv_im_ac=piv_im.merge(df_ac, left_on='NUMERO DA SUBFATURA',right_on='NUMERO DA SUBFATURA',how='left')
    #criando uma coluna valor de taxa / quantidade de pessoas incluidas
    piv_im_ac['CARTAO__TAXA_DE_IMPLANTACAO']=piv_im_ac['VALOR DO LANCAMENTO']/piv_im_ac['TIPO DE LANÇAMENTO_x']
    #removendo subfaturas que não tiveram lançamento de taxa
    piv_im_ac=piv_im_ac[piv_im_ac['CARTAO__TAXA_DE_IMPLANTACAO'].notnull()]
    #juntando os valores de taxa com a tabela original
    df_fm_3_p=df_fm_3.merge(piv_im_ac, left_on='NUMERO DA SUBFATURA',right_on='NUMERO DA SUBFATURA',how='left')
    #removendo valores de quem não é inclusão mês
    df_fm_3_p.loc[df_fm_3_p['TIPO DE LANÇAMENTO']!='IM','CARTAO__TAXA_DE_IMPLANTACAO']=0
    #zera as linhas de taxa na coluna de valor do lancamento
    df_fm_3_p.loc[df_fm_3_p['NOME SEGURADO/DEPENDENTE_x']=='COB.REF. TAXA IMPLANTACAO','VALOR DO LANCAMENTO_x']=0###
    #zera valores nulos
    df_fm_3_p['CARTAO__TAXA_DE_IMPLANTACAO']=df_fm_3_p['CARTAO__TAXA_DE_IMPLANTACAO'].fillna(0)

    df_fm_3_p['IOF']=(df_fm_3_p['VALOR DO LANCAMENTO_x'])*iof
    df_fm_3_p['IOF']=df_fm_3_p['IOF'].fillna(0)

    df_fm_3_p['IOF_TAXA']=df_fm_3_p['CARTAO__TAXA_DE_IMPLANTACAO']*iof#
    df_fm_3_p['IOF_TAXA']=df_fm_3_p['IOF_TAXA'].fillna(0)#
    
    df_fm_3_p['CARTAO___TAXA_DE_IMPLANTACAO']= df_fm_3_p['IOF_TAXA']+df_fm_3_p['CARTAO__TAXA_DE_IMPLANTACAO']

    df_fm_3_p['TOTAL_GERAL']=df_fm_3_p['VALOR DO LANCAMENTO_x']+df_fm_3_p['IOF']#+df_fm_3_p['CARTAO__TAXA_DE_IMPLANTACAO']+df_fm_3_p['IOF_TAXA']

    df_fm_3_p=df_fm_3_p[df_fm_3_p['NUMERO DO CERTIFICADO']!='0000000'].copy()

    convert_dict={'NUMERO DA SUBFATURA':int,
                'NUMERO DO CERTIFICADO':int}
    df_fm_3_p=df_fm_3_p.astype(convert_dict) 

    #piv_3=pd.pivot_table(df_fm_3_p.round({'VALOR DO LANCAMENTO_x':2,'IOF':2}),values=['CARTAO__TAXA_DE_IMPLANTACAO','VALOR DO LANCAMENTO_x','IOF','TOTAL_GERAL'],index='NUMERO DA SUBFATURA',aggfunc=[np.sum])

    print(df_fm_3_p.shape)

    df_fm=df_fm_3_p.drop(['N1','TIPO DE LANÇAMENTO_x','NOME SEGURADO/DEPENDENTE_y','TIPO DE LANÇAMENTO_y','VALOR DO LANCAMENTO_y'],axis=1).copy()
    
    df_fm=df_fm.rename(columns={'NOME SEGURADO/DEPENDENTE_x': 'NOME SEGURADO/DEPENDENTE',
                                'VALOR DO LANCAMENTO_x': 'VALOR DO LANCAMENTO'
    
    })

    print(df_fm.shape)
    return df_fm

def tabela_pc(pc):
    cols_pc=['TIPO DE REGISTRO','NUMERO DA SUBFATURA','NUMERO DO CERTIFICADO','NOME DO SEGURADO',
    'NUMERO DA MATRICULA','SEXO DO SEGURADO','DATA DE NASCIMENTO','ESTADO CIVIL','NUMERO DO CPF',
    'CARGO DE OCUPAÇÃO','DATA DE ADMISSAO','DATA DE INICIO DE VIGENCIA','PLANO','MATRICULA ESPECIAL',
    'DATA DE NASCIMENTO (Y2K)','DATA DE ADMISSAO (Y2K)','DATA DE INICIO DE VIGENCIA (Y2K)','AREA RESERVADA',
    'DATA DE REATIVAÇÃO','REGIÃO','DATA DE CANCELAMENTO (Y2K)']

    col_specification = [(0, 1), (1,4),(4,11),(11,46),(46,57),(57,58),(58,64),(64,65),(65,76)
                        ,(76,96),(96,102),(102,108),(108,112),(112,124),(124,132),(132,140),(140,148),(148,156),(156,160),(160,168),(168,177)]
    df_pc_titular=pd.read_fwf(pc, colspecs=col_specification,skiprows=0,header=None)

    df_pc_titular.columns=cols_pc

    df_pc_titular_2=df_pc_titular[df_pc_titular['TIPO DE REGISTRO']=='2']

    print(df_pc_titular_2.shape)
    return df_pc_titular_2



