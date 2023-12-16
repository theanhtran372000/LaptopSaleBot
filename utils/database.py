import yaml
import mysql.connector
from loguru import logger


def mysql_connect(configs):
    try:
        connection = mysql.connector.connect(
            host=configs['mysql']['host'],
            database=configs['mysql']['db'],
            user=configs['mysql']['user'],
            password=configs['mysql']['pass']
        )

        if connection.is_connected():
            return connection
        else:
            return None

    except:
        logger.exception("Can't connect to MySQL!")
        return None
    
def filter_select(
    configs,
    branch=None, 
    ram=None,
    cpu=None,
    os=None,
    min_price=None,
    max_price=None,
    discount=False,
    purpose=None
):
    # Get DB cursor
    connection = mysql_connect(configs)
    cursor = connection.cursor()
    
    if not cursor:
        return None
    
    conditions = []
    
    if branch:
        conditions.append('branch="{}"'.format(branch))
    if ram:
        conditions.append('ram="RAM {} GB"'.format(ram))
    if cpu:
        conditions.append('cpu like "%{}%"'.format(cpu))
    if os:
        conditions.append('os="{}"'.format(os))
    if min_price:
        conditions.append('new_price >= {}'.format(min_price))
    if max_price:
        conditions.append('new_price <= {}'.format(max_price))
    if discount:
        conditions.append('discount is not null')
    if purpose:
        if purpose == 'Gaming':
            conditions.append('gpu like "%Card rời%" AND (size like "%Nặng 2.%" OR size like "%Nặng 3.%")')
        if purpose == 'Graphic':
            conditions.append('gpu like "%Card rời%" AND size like "%Nặng 1.%"')
        if purpose == 'Office':
            conditions.append('gpu like "%Card tích hợp%"')
    
    if len(conditions) > 0:
        select_query = '''
            SELECT * FROM products
            WHERE {}
        '''.format(' AND '.join(conditions))
    else:
        select_query = '''
            SELECT * FROM products
        '''
        
    cursor.execute(select_query)
    
    # Fetch all rows from the result set
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return result
        
if __name__ == '__main__':
    with open('/home/asus/work/LaptopSaleBot/configs.yml') as f:
        configs = yaml.full_load(f)
    
    # cursor = mysql_connect(configs)    
    # print(cursor)
    
    result = filter_select(
        configs,
        branch='HP',
        purpose='Gaming',
        discount=True
    )
    
    for i, e in enumerate(result[0]):
        print('{}: {}'.format(i, e))
    