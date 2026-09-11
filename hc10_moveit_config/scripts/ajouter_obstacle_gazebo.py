#!/usr/bin/env python3
"""
Ajoute un obstacle statique dans Gazebo Harmonic pendant que la simulation tourne.

IMPORTANT :
La pose monde est passée explicitement à `ros_gz_sim create` avec
--x/--y/--z. Le SDF garde donc une pose locale nulle.

Par défaut :
  world       = room_315_only
  partition   = room315_moveit
  name        = camera_test_obstacle
  x           = -14.559
  y           = -3.465
  dimensions  = 0.40 x 0.40 x 1.00 m
  z           = size_z / 2  (la boîte repose sur le sol)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="Ajoute une boîte statique dans Gazebo Harmonic."
    )
    p.add_argument("--world", default="room_315_only")
    p.add_argument("--partition", default="room315_moveit")
    p.add_argument("--name", default="camera_test_obstacle")

    p.add_argument("--x", type=float, default=-14.559)
    p.add_argument("--y", type=float, default=-3.465)
    p.add_argument(
        "--z",
        type=float,
        default=None,
        help="Centre Z de la boîte. Défaut : size_z/2.",
    )

    p.add_argument("--roll", type=float, default=0.0)
    p.add_argument("--pitch", type=float, default=0.0)
    p.add_argument("--yaw", type=float, default=0.0)

    p.add_argument("--size-x", type=float, default=0.40)
    p.add_argument("--size-y", type=float, default=0.40)
    p.add_argument("--size-z", type=float, default=1.00)

    return p.parse_args()


def main():
    args = parse_args()

    if shutil.which("ros2") is None:
        print(
            "ERREUR : `ros2` introuvable. "
            "Fais `source /opt/ros/jazzy/setup.bash`.",
            file=sys.stderr,
        )
        return 1

    for value, label in (
        (args.size_x, "size-x"),
        (args.size_y, "size-y"),
        (args.size_z, "size-z"),
    ):
        if value <= 0:
            print(f"ERREUR : --{label} doit être > 0.", file=sys.stderr)
            return 1

    z = args.z if args.z is not None else args.size_z / 2.0

    # La pose du modèle reste locale / nulle.
    # La pose monde est donnée à ros_gz_sim create ci-dessous.
    sdf = f"""<?xml version="1.0"?>
<sdf version="1.9">
  <model name="{args.name}">
    <static>true</static>

    <link name="obstacle_link">
      <collision name="obstacle_collision">
        <geometry>
          <box>
            <size>{args.size_x} {args.size_y} {args.size_z}</size>
          </box>
        </geometry>
      </collision>

      <visual name="obstacle_visual">
        <geometry>
          <box>
            <size>{args.size_x} {args.size_y} {args.size_z}</size>
          </box>
        </geometry>
        <material>
          <ambient>0.9 0.1 0.1 1</ambient>
          <diffuse>0.9 0.1 0.1 1</diffuse>
          <specular>0.2 0.2 0.2 1</specular>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

    env = os.environ.copy()
    env["GZ_PARTITION"] = args.partition

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".sdf",
        prefix=f"{args.name}_",
        delete=False,
    ) as f:
        f.write(sdf)
        sdf_path = Path(f.name)

    cmd = [
        "ros2", "run", "ros_gz_sim", "create",
        "--world", args.world,
        "--file", str(sdf_path),
        "--name", args.name,
        "--x", str(args.x),
        "--y", str(args.y),
        "--z", str(z),
        "--roll", str(args.roll),
        "--pitch", str(args.pitch),
        "--yaw", str(args.yaw),
    ]

    print("Ajout de l'obstacle dans Gazebo...")
    print(f"  world      : {args.world}")
    print(f"  partition  : {args.partition}")
    print(f"  name       : {args.name}")
    print(f"  position   : x={args.x:.3f}, y={args.y:.3f}, z={z:.3f}")
    print(
        f"  dimensions : "
        f"{args.size_x:.3f} x {args.size_y:.3f} x {args.size_z:.3f} m"
    )

    try:
        result = subprocess.run(cmd, env=env, check=False)
    finally:
        try:
            sdf_path.unlink()
        except FileNotFoundError:
            pass

    if result.returncode != 0:
        print(
            "\nÉchec du spawn. Vérifie Gazebo, le world et GZ_PARTITION.",
            file=sys.stderr,
        )
        return result.returncode

    print("\nObstacle ajouté.")
    print(
        "Vérification conseillée :\n"
        f"  export GZ_PARTITION={args.partition}\n"
        f"  gz model -m {args.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
