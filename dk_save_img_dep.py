from projectaria_tools.core.stream_id import StreamId
from projectaria_tools.core import calibration
from projectaria_tools.projects.adt import (
   AriaDigitalTwinDataProvider,
   AriaDigitalTwinSkeletonProvider,
   AriaDigitalTwinDataPathsProvider,
   bbox3d_to_line_coordinates,
   bbox2d_to_image_coordinates,
   utils as adt_utils,
)
import ipdb
import os
import re
from tqdm import tqdm
import numpy as np
import json
import cv2
import matplotlib.pyplot as plt
import open3d as o3d

from cam_utils.camera import Fisheye624
import torch




# ADIL
BASE_PATH = "./temp/"
# SEQUENCE_NAME = "Apartment_release_golden_skeleton_seq100_M1292"
# SEQUENCE_NAME = "Apartment_release_meal_skeleton_seq135_M1292"
SEQUENCE_NAME = "Apartment_release_work_skeleton_seq109_M1292"

OUT_PATH = "./processed_data" 

sequence_path = os.path.join(BASE_PATH, SEQUENCE_NAME)

scene_mps_path = os.path.join(sequence_path, "mps", "slam")
scene_image_path = os.path.join(sequence_path, "214-1")
scene_image_list = [name for name in os.listdir(scene_image_path) if name.endswith(".jpg")]
scene_image_list.sort(key=lambda name: int(re.search(r"-(\d{5})-", name).group(1)))

paths_provider = AriaDigitalTwinDataPathsProvider(sequence_path)
data_paths = paths_provider.get_datapaths()
gt_provider = AriaDigitalTwinDataProvider(data_paths)

stream_id = StreamId("214-1")
camera_calibration = gt_provider.get_aria_camera_calibration(stream_id)
T_Device_Cam = camera_calibration.get_transform_device_camera()

img_timestamps_ns_all = gt_provider.get_aria_device_capture_timestamps_ns(stream_id)


# # JAEHOON
# JH_ROOT_PATH = "/fs/nexus-projects/ANYCAM/ADT/{}".format("_".join(SEQUENCE_NAME.split("_")[:-1]))
# JH_JSON_FILE = "transforms.json"
# with open(os.path.join(JH_ROOT_PATH, JH_JSON_FILE), 'r') as f:
#     JH_DATA = json.load(f)
#     frames = JH_DATA['frames']
#     frames = sorted(frames, key=lambda x: x['image_path'])
#     JH_DATA['frames'] = frames


# JH_DATA['camera_model'] = 'Fisheye624'

# debug
points_list = []
colors_list = []

ii = 0
for i,scene_image in tqdm(enumerate(scene_image_list), total=len(scene_image_list)):

    # if i % 100 != 0:
    #     continue

    FILE_DICT = {}
    FILE_DICT['filepath'] = os.path.join(sequence_path, '214-1', scene_image)

    timestamp = img_timestamps_ns_all[i]
    # print(f"Image: {scene_image}, Timestamp (ns): {timestamp}")
    aria_pose_with_dt = gt_provider.get_aria_3d_pose_by_timestamp_ns(timestamp)

    if not aria_pose_with_dt.is_valid:
        print(f"WARNING: No Aria poses for timestamp {timestamp}, skipping image {scene_image}")
    
        continue
    
    T_Scene_Device = aria_pose_with_dt.data().transform_scene_device
    pose_c2w = T_Scene_Device @ T_Device_Cam
    pose_c2w = pose_c2w.to_matrix()

    projection_params = camera_calibration.get_projection_params().tolist()
    fx = camera_calibration.get_focal_lengths().tolist()[0]
    cam_params = [fx] + projection_params


    # debug
    # image_path = JH_DATA['frames'][i]['image_path']
    # depth_path = image_path.replace("images", "depths").replace("rgb", "depth").replace(".jpg", ".png")

    # image = cv2.imread(os.path.join(JH_ROOT_PATH, image_path), -1)[..., ::-1]
    image = gt_provider.get_aria_image_by_timestamp_ns(timestamp, stream_id).data().to_numpy_array()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    orig_h, orig_w = image.shape[:2]

    # depth = cv2.imread(os.path.join(JH_ROOT_PATH, depth_path), -1) / 1000.
    depth = gt_provider.get_depth_image_by_timestamp_ns(timestamp, stream_id).data().to_numpy_array() # / 1000.
    depth = depth.astype(np.uint16).clip(max=65535)


    # save image and depth
    os.makedirs(os.path.join(OUT_PATH, SEQUENCE_NAME, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUT_PATH, SEQUENCE_NAME, "depths"), exist_ok=True)
    image_output_path = os.path.join(OUT_PATH, SEQUENCE_NAME, "images", f"{timestamp}.png")
    depth_output_path = os.path.join(OUT_PATH, SEQUENCE_NAME, "depths", f"{timestamp}.png")
    cv2.imwrite(image_output_path, image)
    cv2.imwrite(depth_output_path, depth)







#     # target_h, target_w = 336, 518
#     target_h, target_w = 224, 224
#     image = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
#     depth = cv2.resize(depth, (target_w, target_h), interpolation=cv2.INTER_NEAREST)
#     camera = Fisheye624(params=torch.tensor(cam_params).float())
#     factor_x = target_w / orig_w
#     factor_y = target_h / orig_h 
#     camera.resize_v2(factor_x, factor_y)

#     rays = camera.get_rays([1, target_h, target_w])     # [1, 3, h, w]
#     c_points= camera.reconstruct(torch.from_numpy(depth)).reshape(1*3, -1)
#     w_points = torch.from_numpy(pose_c2w) @ torch.cat([c_points, torch.ones((1, c_points.shape[-1]))], dim=0)
#     w_points = w_points[:3].T  # [N, 3]

#     colors = torch.from_numpy(image.reshape(-1, 3)) / 255.    # [N, 3]

#     points_list.append(w_points)
#     colors_list.append(colors)
#     ii += 1

#     if ii > 40:
#         break

# points = torch.cat(points_list, dim=0).numpy()
# colors = torch.cat(colors_list, dim=0).numpy()
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points.astype(np.float64))
# pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float64))
# o3d.io.write_point_cloud("trash.ply", pcd)
# ipdb.set_trace()







    # JH_DATA['frames'][i]['transform_matrix'] = pose_c2w.tolist()
    # JH_DATA['frames'][i]['fx'] = cam_params[0]
    # JH_DATA['frames'][i]['fy'] = cam_params[1]
    # JH_DATA['frames'][i]['cx'] = cam_params[2]
    # JH_DATA['frames'][i]['cy'] = cam_params[3]
    # JH_DATA['frames'][i]['k1'] = cam_params[4]
    # JH_DATA['frames'][i]['k2'] = cam_params[5]
    # JH_DATA['frames'][i]['k3'] = cam_params[6]
    # JH_DATA['frames'][i]['k4'] = cam_params[7]
    # JH_DATA['frames'][i]['k5'] = cam_params[8]
    # JH_DATA['frames'][i]['k6'] = cam_params[9]
    # JH_DATA['frames'][i]['p1'] = cam_params[10]
    # JH_DATA['frames'][i]['p2'] = cam_params[11]
    # JH_DATA['frames'][i]['s1'] = cam_params[12]
    # JH_DATA['frames'][i]['s2'] = cam_params[13]
    # JH_DATA['frames'][i]['s3'] = cam_params[14]
    # JH_DATA['frames'][i]['s4'] = cam_params[15]
