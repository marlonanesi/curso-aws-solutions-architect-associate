FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY handler.py ${LAMBDA_TASK_ROOT}

CMD ["handler.lambda_handler"]
