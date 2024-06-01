from django.http import JsonResponse
from .models import Number
import requests
import time
import statistics
from collections import deque
import threading

test_server_url = ' http://localhost:8000/numbers/p/'
window_size = 10
numbers_queue = deque(maxlen=window_size)
lock = threading.Lock()

def get_numbers(request, numberid):
    if numberid not in ['p', 'f', 'e', 'r']:
        return JsonResponse({'error': 'Invalid number ID'}, status=400)

    start_time = time.time()
    with lock:
        if time.time() - start_time > 0.5:
            return JsonResponse({'error': 'Request timeout exceeded'}, status=500)

        response = requests.get(f'{test_server_url}/{numberid}')
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch numbers from the test server'}, status=500)

        received_numbers = response.json()['numbers']
        unique_numbers = set(received_numbers) - set(numbers_queue)

        for num in unique_numbers:
            Number.objects.get_or_create(value=num)

        numbers_queue.extend(unique_numbers)

        window_prev_state = list(numbers_queue)[:-len(unique_numbers)]
        window_curr_state = list(numbers_queue)

        avg = statistics.mean(numbers_queue) if numbers_queue else 0

        return JsonResponse({
            'numbers': received_numbers,
            'windowPrevState': window_prev_state,
            'windowCurrState': window_curr_state,
            'avg': avg
        }, status=200)

