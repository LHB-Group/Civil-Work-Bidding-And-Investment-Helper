def re_category (ds,counts, repl_ ):
    """
        It replaces the categories that are not sufficiently presented in the dataseries
        It also fills NaN values with the defined category value
    """
    n_count = ds.value_counts()
    m_ng = ds.isin (n_count.index[n_count.values < counts])
    ds[m_ng] = repl_
    ds.fillna(repl_,inplace=True)
    return ds.astype('str')


def text_split(x):
    """ 
        x will be sth similar to 'erect a two story 88 unit residential structure'
        we do text partition with 'story' 
        it returns tuple ('erect a two ', 'story', ' 88 unit residential structure')
        then, we take the first value of tuple 
        and then apply string manipulations to obtain floor number in text
    """
    return x.partition('story')[0].replace('-',' ').split(' ')[-2]


def text2int (x):
    """
        converting text to number for the possible cases
    """
    x = x.lower()
    if 'one' in x:
        y = 1
    elif 'two' in x:
        y= 2
    elif 'three' in x:
        y=3
    elif 'four' in x:
        y = 4
    elif 'five' in x:
        y = 5
    elif 'six' in x:
        y = 6
    elif 'seven' in x:
        y = 7
    elif 'eight' in x:
        y = 8
    elif 'nine' in x:
        y = 9
    elif  'ten' in x:
        y = 10
    elif  'eleven' in x:
        y = 11
    else:
        try : 
            y = int(x)
        except :
            y = np.nan
    return y



def cat_stories (st): 
    """
    adding a column with story number categories
    """   
    if st < 3 :
      y = '0-2 stories'
    elif st< 5 :
      y = '3-4 stories'
    elif st < 8 :
      y = '5-7 stories'
    elif st < 10 :
      y = '8-9 stories'
    else:
      y = 'More than 10 stories'
    return y