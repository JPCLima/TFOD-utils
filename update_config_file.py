import argparse
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
import os

# Initiate argument parser
parser = argparse.ArgumentParser(
    description="Update config file")

parser.add_argument("-w",
                    "--network_architecture",
                    help="Neuro network architecture")

parser.add_argument("-p",
                    "--pipeline_config",
                    help="path to config file")

parser.add_argument("-m",
                    "--label_map",
                    help="path to labelmap file")

parser.add_argument("-t",
                    "--pre_model_path",
                    help="path to pretrained model folder")

parser.add_argument("-n",
                    "--pre_model_name",
                    help="path to pretrained name")

parser.add_argument("-a",
                    "--annotation_path",
                    help="path to annotation folder")

parser.add_argument("-c",
                    "--num_classes",
                    type=int,
                    help="number of classes")

parser.add_argument("-b",
                    "--batch_size",
                    type=int,
                    help="Batch size")

args = parser.parse_args()


def update_config(network_architecture, config_path, labelmap_path, pretrained_path,
                  pretrained_model_name, annotation_path, num_classes, batch_size):

    config = config_util.get_configs_from_pipeline_file(config_path)

    pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
    with tf.io.gfile.GFile(config_path, "r") as f:
        proto_str = f.read()
        text_format.Merge(proto_str, pipeline_config)

    print(network_architecture)

    # Choose architecture
    if (network_architecture == 'sdd'):
        pipeline_config.model.ssd.num_classes = num_classes
    elif (network_architecture == 'center_net'):
        pipeline_config.model.center_net.num_classes = num_classes
    elif (network_architecture == 'faster_rcnn'):
        pipeline_config.model.faster_rcnn.num_classes = num_classes


    # Modify config file
    pipeline_config.train_config.batch_size = batch_size
    pipeline_config.train_config.fine_tune_checkpoint = os.path.join(
        pretrained_path, pretrained_model_name, 'checkpoint', 'ckpt-0')
    pipeline_config.train_config.fine_tune_checkpoint_type = "detection"
    pipeline_config.train_input_reader.label_map_path = labelmap_path
    pipeline_config.train_input_reader.tf_record_input_reader.input_path[:] = [
        os.path.join(annotation_path, 'train.record')]
    pipeline_config.eval_input_reader[0].label_map_path = labelmap_path
    pipeline_config.eval_input_reader[0].tf_record_input_reader.input_path[:] = [
        os.path.join(annotation_path, 'test.record')]

    # Write in the file
    config_text = text_format.MessageToString(pipeline_config)
    with tf.io.gfile.GFile(config_path, "wb") as f:
        f.write(config_text)


if __name__ == '__main__':
    try:
        update_config(args.network_architecture, args.pipeline_config, args.label_map, args.pre_model_path,
                      args.pre_model_name, args.annotation_path, args.num_classes, args.batch_size)
        print('Config file updated Successfully!!!')
    except Exception as e:
        print(e)
