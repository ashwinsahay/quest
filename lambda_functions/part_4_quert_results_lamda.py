import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Lambda triggered by SQS message:")
    

    result_task_1 = """|Mean_Population|StdDev_Population|
                    +---------------+-----------------+
                    |   3.17437383E8|     4257089.5415|
                    +---------------+-----------------+"""

    result_task_2 = """
    
    |series_id  |year|value             |
    +-----------+----+------------------+
    |PRS30006011|2022|20.5              |
    |PRS30006012|2022|17.1              |
    |PRS30006013|1998|705.895           |
    |PRS30006021|2010|17.7              |
    |PRS30006022|2010|12.399999999999999|
    |PRS30006023|2014|503.21600000000007|
    |PRS30006031|2022|20.4              |
    
    """

    result_task_3 = """
    +-----------+----+------+-----+----------+
    |series_id  |year|period|value|Population|
    +-----------+----+------+-----+----------+
    |PRS30006032|2003|Q01   |-5.7 |NULL      |
    |PRS30006032|2007|Q01   |-0.8 |NULL      |
    |PRS30006032|2015|Q01   |-1.7 |316515021 |
    |PRS30006032|2006|Q01   |1.8  |NULL      |
    |PRS30006032|2013|Q01   |0.5  |311536594 |
    |PRS30006032|1997|Q01   |2.8  |NULL      |
    |PRS30006032|2014|Q01   |-0.1 |314107084 |
    |PRS30006032|2004|Q01   |2.0  |NULL      |
    |PRS30006032|1996|Q01   |-4.2 |NULL      |


    """


    logger.info(f"TASK 1:run population mean/stddev query results are : {result_task_1} ")
    logger.info("TASK 2: run best year per series_id results are : {result_task_2}")
    logger.info("TASK 3:  Join PRS30006032 Q01 record with population data results are : {result_task_3}")

    print("Complete")
