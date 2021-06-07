import threading
import logging

message_format = '%(asctime)s: %(message)s'
logging.basicConfig(format=message_format, level=logging.INFO, datefmt='%H:%M:%S')


def test_function(argument):
    logging.info(f"Method executed {argument}")


my_task = threading.Thread(target=test_function, args=(10, ))
my_task.start()
