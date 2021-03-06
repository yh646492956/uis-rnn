# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from model import arguments
from model import evals
from model import uisrnn
from model import utils
import numpy as np

SAVED_MODEL_NAME = 'saved_model.uisrnn'


def diarization_experiment(model_args, training_args, inference_args):
  """Experiment pipeline.

  Load data --> train model --> test model --> output result

  Args:
    model_args: model configurations
    training_args: training configurations
    inference_args: inference configurations
  """

  predicted_labels = []
  test_record = []

  train_data = np.load('./data/training_data.npz')
  test_data = np.load('./data/testing_data.npz')
  train_sequence = train_data['train_sequence']
  train_cluster_id = train_data['train_cluster_id']
  test_sequences = test_data['test_sequences']
  test_cluster_ids = test_data['test_cluster_ids']

  model = uisrnn.UISRNN(model_args)

  # training
  model.fit(train_sequence, train_cluster_id, training_args)
  model.save(SAVED_MODEL_NAME)
  # we can also skip training by calling：
  # model.load(SAVED_MODEL_NAME)

  # testing
  for (test_sequence, test_cluster_id) in zip(test_sequences, test_cluster_ids):
    predicted_label = model.predict(test_sequence, inference_args)
    predicted_labels.append(predicted_label)
    accuracy = evals.compute_sequence_match_accuracy(
        test_cluster_id, predicted_label)
    test_record.append((accuracy, len(test_cluster_id)))
    print('Ground truth labels:')
    print(test_cluster_id)
    print('Predicted labels:')
    print(predicted_label)
    print('-' * 80)

  output_string = utils.output_result(model_args, training_args, test_record)

  print('Finished diarization experiment')
  print(output_string)


def main():
  model_args, training_args, inference_args = arguments.parse_arguments()
  diarization_experiment(model_args, training_args, inference_args)


if __name__ == '__main__':
  main()
