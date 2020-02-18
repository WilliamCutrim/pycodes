import pandas as pd
import numpy as np

def faturas_sul_america(file_list):
    df_all=[]
    cols=('Codigo','Nome','CPF','Nascimento','Grau parentesco','Vigencia','Plano','Valor 2ª via','Valor')
    #for file in file_list:
    try:
        #df=pd.read_excel(file,header=None,skiprows=19)            
        df=pd.read_excel(file_list,header=None,skiprows=19,dtype={0:object,6:object})
        df_fatura_name=pd.read_excel(file_list,header=None,skiprows=0,dtype={0:object,6:object})

        df_filter=df[[1,3,6,9,12,18,20,29,33]]
        df_filter_notnull=df_filter[df_filter[20].notnull()]
        df_filter_notnull.columns=cols
        df_filter_notnull['sub']=df_fatura_name[6].iloc[4]
        df_filter_notnull['empresa']=str(df_fatura_name[11].iloc[15]).replace('.0','')
        df_all.append(df_filter_notnull)

        #separando 're'
        df_sep_re=df[[0,3,12,17,31]][df[0].notnull()]
        matr=[]
        for i in df_sep_re[12]:
            comeco=i.find(' ')
            fim=len(i)
            re=i[comeco:fim]
            matr.append(re)
        df_sep_re['Matricula']=matr
        df_sep_re[0] = [str(cod) for cod in df_sep_re[0]]
        #print(df.shape, 'Deu certo', file)
        #print(df_sep_re.shape, 'Apenas titulares', file)
    except:
        #falta separar o re no except, porém não tenho o modelo do arquivo antigo
        df=pd.read_excel(file_list,header=None,skiprows=19,dtype={0:object})
        df_filter=df[[0,4,8,11,14,18,20,27,32]]
        df_filter_notnull=df_filter[df_filter[20].notnull()]
        df_filter_notnull.columns=cols
        df_filter_notnull['sub']=file_list
        df_all.append(df_filter_notnull)
        #print('Meh', file)

    df_all_concat=pd.concat(df_all,axis=0)

    #quebrando o codigo em grupo familiar e parentesco para merge
    list_grupo_familiar=[]
    list_cod_parentesco=[]
    for i in df_all_concat['Codigo']:
        fim_a=len(str(i))
        # grupo_familiar=str(i)[0:7]
        # cod_parentesco=str(i)[7:9]
        grupo_familiar=str(i)[0:-2]
        cod_parentesco=str(i)[-2:fim_a]
                
        list_grupo_familiar.append(grupo_familiar)
        list_cod_parentesco.append(cod_parentesco)
    df_all_concat['Grupo Famila']=list_grupo_familiar
    df_all_concat['Cod Parentesco']=list_cod_parentesco
    #merge para conseguir a matricula
    df_all_concat_re=df_all_concat.merge(df_sep_re[[0,3,'Matricula',17]],left_on='Grupo Famila',right_on=0,how='left')
    df_all_concat_re=df_all_concat_re.drop([0],axis=1)

    df_cpf_titular=df_all_concat_re[['Nome','CPF','Grupo Famila']].loc[df_all_concat_re['Grau parentesco']=='TITULAR']

    df_all_concat_re_a=df_all_concat_re.merge(df_cpf_titular,left_on='Grupo Famila',right_on='Grupo Famila',how='left')
    df_all_concat_re_b=df_all_concat_re_a.rename(columns={'CPF_x':'CPF',
                                     'CPF_y':'CPF Titular',
                                     'Nome_x':'Beneficiario',
                                     'Nome_y':'Titular',
                                      17:'Setor'}
    )
    return df_all_concat_re_b

#Acerto
def arquivo_acerto(acerto):
    df_acerto=pd.read_excel(acerto,header=None,skiprows=11)
    df_acerto_name=pd.read_excel(acerto,header=None,skiprows=0)
    #df_acerto_name[1].iloc[7]
    inicio=df_acerto_name[1].iloc[7].find('-')
    fim=len(df_acerto_name[1].iloc[7])

    inicio_2=df_acerto_name[1].iloc[7].find(':')
    fim_2=df_acerto_name[1].iloc[7].find('-')

    #df_acerto[[1,6,9,11,12]]
    df_acerto_filter=df_acerto[[1,6,9,11,12]]
    df_filter_notnull=df_acerto_filter[df_acerto_filter[11].notnull()]
    df_filter_notnull
    #iof=0.0238
    Tipo=[]
    Matricula=[]
    Segurado=[]
    Competencia=[]

    for i in df_filter_notnull[1]:
        a=str(i).split('-')
        if len(a)>1:
            Tipo.append(a[0])
            Matricula.append(a[1])
            Segurado.append(a[2].lstrip().rstrip())
            Competencia.append(a[3])
        else:
            Tipo.append(a[0])
            Matricula.append(a[0])
            Segurado.append(a[0].lstrip().rstrip())
            Competencia.append(a[0])

    df_filter_notnull['Plano']=Tipo
    df_filter_notnull['Codigo']=Matricula
    df_filter_notnull['Nome']=Segurado
    df_filter_notnull['Competencia']=Competencia
    df_filter_notnull['sub']=df_acerto_name[1].iloc[7][inicio+2:fim]
    df_filter_notnull['empresa']=df_acerto_name[1].iloc[7][inicio_2+2:fim_2].rstrip().lstrip()
    df_filter_notnull=df_filter_notnull.rename(columns={
                                                    6: 'Matricula',
                                                    9: 'Acerto',
                                                    11: 'Percentual',
                                                    12: 'Tipo Operação'
                                                })
    df_filter_notnull=df_filter_notnull.drop([1],axis=1)

    return df_filter_notnull


def read_boleto_sa(pdf):
    print('Iniciando leitura dos boletos. Aguarde alguns segundos...')
    try:
        dict_boletos={'Valor_boleto':[],'Empresa':[],'CNPJ':[],'Vencimento':[]}

        df_emp_cnpj=read_pdf(pdf, multiple_tables=True,stream=True, pages=0, area=(114.963,50.152,177.467,373.833))
        df_concat_df_emp_cnpj=pd.concat(df_emp_cnpj,axis=0)

        df=read_pdf(pdf, multiple_tables=True,stream=True, pages=0, area=(114.219,376.065,149.191,551.672))
        df_concat_vencimento=pd.concat(df,axis=0)

        df=read_pdf(pdf, multiple_tables=True,stream=True, pages=0, area=(175.978,376.065,213.183,551.672))
        df_concat_valor=pd.concat(df,axis=0)
        #empresa
        empresa=df_concat_df_emp_cnpj[df_concat_df_emp_cnpj.columns[0]].iloc[0]
        #cnpj
        cnpj=df_concat_df_emp_cnpj[df_concat_df_emp_cnpj.columns[0]].iloc[2]
        #valor
        valor=df_concat_valor[df_concat_valor.columns[0]].iloc[0]
        #vencimento
        vencimento=df_concat_vencimento[df_concat_vencimento.columns[1]].iloc[0]

        dict_boletos['Empresa'].append(empresa)
        dict_boletos['CNPJ'].append(cnpj)
        dict_boletos['Valor_boleto'].append(valor)
        dict_boletos['Vencimento'].append(vencimento)
        rateio_boletos=pd.DataFrame(dict_boletos)
    except:
        print('Arquivo fora de padrão ou não é um PDF')
    return rateio_boletos