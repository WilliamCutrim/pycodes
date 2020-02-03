def faturas_sul_america(file_list):
    df_all=[]
    cols=('Codigo','Nome','CPF','Nascimento','Grau parentesco','Vigencia','Plano','Valor 2ª via','Valor')
    #for file in file_list:
    try:
        #df=pd.read_excel(file,header=None,skiprows=19)            
        df=pd.read_excel(file_list,header=None,skiprows=19,dtype={0:object})
        df_filter=df[[1,3,6,9,12,18,20,29,33]]
        df_filter_notnull=df_filter[df_filter[20].notnull()]
        df_filter_notnull.columns=cols
        df_filter_notnull['sub']=file_list
        #df_filter_notnull['sub']=file
        df_all.append(df_filter_notnull)

        #separando re
        df_sep_re=df[[0,3,12,31]][df_test[0].notnull()]
        matr=[]
        for i in df_sep_re[12]:
            comeco=i.find(' ')
            fim=len(i)
            re=i[comeco:fim]
            #print(i,i.find('Re: '),re)
            matr.append(re)
        df_sep_re['Matricula']=matr
        df_sep_re[0] = [str(cod) for cod in df_sep_re[0]]
        print(df.shape, 'Deu certo', file)
        print(df_sep_re.shape, 'Apenas titulares', file)
    except:
        #falta separar o re no except, porém não tenho o modelo do arquivo antigo
        #df=pd.read_excel(file,header=None,skiprows=19)
        df=pd.read_excel(file_list,header=None,skiprows=19,dtype={0:object})
        df_filter=df[[0,4,8,11,14,18,20,27,32]]
        df_filter_notnull=df_filter[df_filter[20].notnull()]
        df_filter_notnull.columns=cols
        df_filter_notnull['sub']=file_list
        #df_filter_notnull['sub']=file
        df_all.append(df_filter_notnull)
        print('Meh', file)

    df_all_concat=pd.concat(df_all,axis=0)

    #quebrando o codigo em grupo familiar e parentesco para merge
    list_grupo_familiar=[]
    list_cod_parentesco=[]
    for i in df_all_concat['Codigo']:
        grupo_familiar=str(i)[0:7]
        cod_parentesco=str(i)[7:9]
        
        list_grupo_familiar.append(grupo_familiar)
        list_cod_parentesco.append(cod_parentesco)
        #print(len(str(i)),i,str(i)[0:7],str(i)[7:9])
    df_all_concat['Grupo Famila']=list_grupo_familiar
    df_all_concat['Cod Parentesco']=list_cod_parentesco
    #merge para conseguir a matricula
    df_all_concat_re=df_all_concat.merge(df_sep_re[[0,3,'Matricula']],left_on='Grupo Famila',right_on=0,how='left')
    df_all_concat_re=df_all_concat_re.drop([0],axis=1)

    # df_all_concat_re=df_all_concat_re.rename(columns={3:'Titular',
    #                         }
    #                     )

    df_cpf_titular=df_all_concat_re[[3,'CPF']].loc[df_all_concat_re['Grau parentesco']=='TITULAR']
    #df_cpf_titular=df_cpf_titular.rename(columns={'CPF':'CPF Titular'})

    df_all_concat_re=df_fatura.merge(df_cpf_titular,left_on='Titular',right_on=3,how='left')
    df_all_concat_re=df_all_concat_re.rename(columns={'CPF_x':'CPF',
                                     'CPF_y':'CPF Titular',
                                     3:'Titular'}
    )
    return df_all_concat_re
