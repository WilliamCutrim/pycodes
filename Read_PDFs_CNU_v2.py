
from tabula import read_pdf
from tabula import convert_into
import pandas as pd
#import PDF_reader_v2 as pdfr

pdf=input('digite o caminho aqui: ')
print('Lendo PDF, aguarde alguns segundos....')
num_pagina=len(read_pdf(pdf, multiple_tables=True,stream=True, pages="all"))/2
print('Número de páginas: ',num_pagina)
#cols=[df_valor.columns[0],df_valor.columns[4]]
print('PDF lido com sucesso')
df_vl=[]
df_pj=[]
df_inf=[]
print('Separando informações.')
for f in range(int(num_pagina)+1):
    print("===============================================================================")
    print('Página: ',f)
    df_CNPJ=read_pdf(pdf,area=(0,0,1000,100),pages=f)
    #selecionando CNPJ
    CNPJ=df_CNPJ[0].loc[[1],df_CNPJ[0].columns[0]]#.values
    #valores
    df_valor=read_pdf(pdf,area=(0,1,1000,1000),pages=f)
    df_v=df_valor[0].loc[(df_valor[0][df_valor[0].columns[0]])=='TOTAL']
    #vencimento
    #df_inf_adicionais=read_pdf(pdf,area=(0,0,1000,1000),pages=f)
    df_inf_a=df_valor[0][df_valor[0].columns[4]].loc[5]#.values
    #appends
    df_pj.append(CNPJ)
    df_vl.append(df_v)
    df_inf.append(df_inf_a)
    print(CNPJ)
    print(df_v)
print('separação concluída.')

# concatenando
pj_concat=pd.concat(df_pj,axis=0)
print('pj_concat feito.')
df_vl_concat=pd.concat(df_vl,axis=0)
print('df_vl_concat feito.')
df_inf_a_concat=pd.DataFrame(data=df_inf,index=None)
print('df_inf feito.')
#substituindo valores nulos
df_vl_concat_fillna=df_vl_concat.fillna('-')
df_inf_a_concat_fillna=df_inf_a_concat.fillna('-')
#separando valores
num_fat=[]
num_rps=[]
data_emissao=[]

#for f in df_inf_a_concat_fillna['Fatura de Serviços'].values:
for f in df_inf_a_concat_fillna[df_inf_a_concat_fillna.columns[0]].values:
    num_fat.append(f[0:9])
    num_rps.append(f[10:17])
    data_emissao.append(f[18:28])

#juntando as duas tabelas
df_vl_concat['CNPJ']=pj_concat.values
#substituindo valores nulos
df_vl_concat_fillna=df_vl_concat.fillna('-')
#juntando valores em uma unica coluna
df_vl_concat_fillna['Valor Total']=df_vl_concat_fillna['Unnamed: 3']+df_vl_concat_fillna['Unnamed: 4']+df_vl_concat_fillna['Unnamed: 5']

ajuste_valor=[]
for f in df_vl_concat_fillna['Valor Total']:
    r1=f.replace("-","")
    r2=r1.replace(".","")
    #r2=float(r1.replace(".","")) could not convert string to float: '12429,69'
    #r3=float(r2.replace(",",".")) 
    ajuste_valor.append(r2)
print('Valores ajustados')

#criando novas colunas
df_vl_concat_fillna['Valor Total']=ajuste_valor
df_vl_concat_fillna['Número da fatura']=num_fat
df_vl_concat_fillna['Número RPS']=num_rps
df_vl_concat_fillna['Data Emissão']=data_emissao
print('Colunas criadas com sucesso.')
#tratando coluna de data
df_inf_a_concat_fillna['Data de vencimento']=(df_inf_a_concat_fillna['Unnamed: 1']+
df_inf_a_concat_fillna['Unnamed: 2']+df_inf_a_concat_fillna['Unnamed: 3']+df_inf_a_concat_fillna['Unnamed: 4'])

data_v_ajustada=[]
for f in df_inf_a_concat_fillna['Data de vencimento']:
    R1=f.replace('-','')
    data_v_ajustada.append(R1[13:])

df_vl_concat_fillna['Data de vencimento']=data_v_ajustada

cols=df_vl_concat_fillna.columns[6:]

output=df_vl_concat_fillna[cols]

output_test=pd.DataFrame(data=output,columns=cols,index=None)[1:340]

#ordenando por CNPJ
output_test=output_test.sort_values(by='CNPJ')

indir='W:/COPARTICIPAÇÃO/Colégio Salesiano/11 Novembro/Arquivos'
salve_name2='test_pdf2.xls' ###alterar essa parte depois
path=indir+'/'+salve_name2

output_test.to_excel(path,index=False)


print('Pronto!')
print('Apresentando Resultado')
output_test


