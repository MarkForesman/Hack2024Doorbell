import logging
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="QueueFunc")
@app.queue_trigger(arg_name="msg", queue_name="queue1",
                   connection="AzureWebJobsStorage")  # Queue trigger
@app.queue_output(arg_name="outputQueueItem", queue_name="queue2",
                 connection="AzureWebJobsStorage")  # Queue output binding
def test_function(msg: func.QueueMessage,
                  outputQueueItem: func.Out[str]) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    outputQueueItem.set('hello')