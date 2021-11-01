import time

MAX_RESULTS = 100

class ResultSet:

    def __init__(self):
      self.data = []
      self.sequence_counter = 0
      self.sequence_start_time = None
      
    def add(self, state):

        # if full dequeue oldest
        if len(self.data) >= MAX_RESULTS:
            self.data.pop(0)

        result = Result(state)

        last_result = self.get_last_value()

        # update the sequence counter iff a last_result exists
        if last_result is not None:
            if last_result.state == result.state:
                if self.sequence_counter == 0:
                    self.sequence_start_time = result.time
                self.sequence_counter += 1
            else:
                self.sequence_counter = 0
                self.sequence_start_time = None
        self.data.append(result)

    def get_last_value(self):
        if len(self.data) == 0:
            return None
        return self.data[-1]

    def get_sequence_duration(self):
        if self.sequence_start_time == None:
            return 0
        return time.time() - self.sequence_start_time

    def clear(self):
        self.data.clear()
        self.sequence_counter = 0
        self.sequence_start_time = None

class Result:

    def __init__(self, state):
        self.state = state
        self.time = time.time()
