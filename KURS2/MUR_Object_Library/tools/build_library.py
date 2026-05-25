#!/usr/bin/env python3
"""
Сборка библиотеки объектов MUR (формат .mur_scene) для курсовой, тема 9.
Сцены совместимы с симулятором MUR (Config.json version 1.0, XML Urho3D).

Пересборка:
  python3 tools/build_library.py
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
NEXT_NODE = 100
NEXT_COMP = 100


def nid() -> int:
    global NEXT_NODE
    NEXT_NODE += 1
    return NEXT_NODE


def cid() -> int:
    global NEXT_COMP
    NEXT_COMP += 1
    return NEXT_COMP


def reset_ids() -> None:
    global NEXT_NODE, NEXT_COMP
    NEXT_NODE = 100
    NEXT_COMP = 100


def vec3(x: float, y: float, z: float) -> str:
    return f"{x} {y} {z}"


def quat_identity() -> str:
    return "1 0 0 0"


def node_open(node_id: int, name: str, pos: Tuple[float, float, float],
              scale: Tuple[float, float, float] = (1, 1, 1),
              rotation: str | None = None) -> str:
    rot = rotation or quat_identity()
    return f"""	<node id="{node_id}">
		<attribute name="Is Enabled" value="true" />
		<attribute name="Name" value="{name}" />
		<attribute name="Tags" />
		<attribute name="Position" value="{vec3(*pos)}" />
		<attribute name="Rotation" value="{rot}" />
		<attribute name="Scale" value="{vec3(*scale)}" />
		<attribute name="Variables" />
"""


def node_close() -> str:
    return "	</node>\n"


def static_model(model: str, material: str) -> str:
    c = cid()
    return f"""		<component type="StaticModel" id="{c}">
			<attribute name="Model" value="Model;{model}" />
			<attribute name="Material" value="Material;{material}" />
		</component>
"""


def scene_environment() -> str:
    """Минимальная подводная среда (как в сценах симулятора)."""
    sky = cid()
    octree = cid()
    debug = cid()
    physics = cid()
    zone_c = cid()
    dir_c = cid()
    floor_c = cid()
    return f"""	<component type="Octree" id="{octree}" />
	<component type="DebugRenderer" id="{debug}" />
	<component type="PhysicsWorld" id="{physics}" />
	<component type="Skybox" id="{sky}">
		<attribute name="Model" value="Model;Models/Box.mdl" />
		<attribute name="Material" value="Material;Materials/Environment/Skybox_PartlyCloudy.xml" />
	</component>
	<node id="{nid()}">
		<attribute name="Is Enabled" value="true" />
		<attribute name="Name" value="lights" />
		<attribute name="Tags" />
		<attribute name="Position" value="0 0 0" />
		<attribute name="Rotation" value="{quat_identity()}" />
		<attribute name="Scale" value="1 1 1" />
		<attribute name="Variables" />
		<node id="{nid()}">
			<attribute name="Is Enabled" value="true" />
			<attribute name="Name" value="AmbientLight" />
			<attribute name="Tags" />
			<attribute name="Position" value="0 2 0" />
			<attribute name="Rotation" value="{quat_identity()}" />
			<attribute name="Scale" value="1 1 1" />
			<attribute name="Variables" />
			<component type="Zone" id="{zone_c}">
				<attribute name="Bounding Box Min" value="-200 -200 -200" />
				<attribute name="Bounding Box Max" value="200 200 200" />
				<attribute name="Ambient Color" value="0.15 0.2 0.25 1" />
				<attribute name="Fog Color" value="0.35 0.55 0.65 1" />
				<attribute name="Fog Start" value="2" />
				<attribute name="Fog End" value="45" />
				<attribute name="Fog Height Scale" value="8" />
				<attribute name="Override Mode" value="true" />
			</component>
		</node>
		<node id="{nid()}">
			<attribute name="Is Enabled" value="true" />
			<attribute name="Name" value="DirectionalLight" />
			<attribute name="Tags" />
			<attribute name="Position" value="0 0 0" />
			<attribute name="Rotation" value="0.453813 0.212742 -0.784503 0.36517" />
			<attribute name="Scale" value="1 1 1" />
			<attribute name="Variables" />
			<component type="Light" id="{dir_c}">
				<attribute name="Light Type" value="Directional" />
				<attribute name="Specular Intensity" value="0.3" />
				<attribute name="Brightness Multiplier" value="0.65" />
				<attribute name="Cast Shadows" value="true" />
			</component>
		</node>
	</node>
	<node id="{nid()}">
		<attribute name="Is Enabled" value="true" />
		<attribute name="Name" value="PoolFloor" />
		<attribute name="Tags" />
		<attribute name="Position" value="0 -2.5 0" />
		<attribute name="Rotation" value="1 0 0 0" />
		<attribute name="Scale" value="30 1 30" />
		<attribute name="Variables" />
		<component type="StaticModel" id="{floor_c}">
			<attribute name="Model" value="Model;Models/Plane.mdl" />
			<attribute name="Material" value="Material;Materials/Pool/TilesDark.xml" />
		</component>
	</node>
"""


def wrap_scene(scene_name: str, object_nodes: str) -> str:
    root_id = nid()
    group_id = nid()
    return f"""<?xml version="1.0"?>
<scene id="1">
	<attribute name="Name" value="{scene_name}" />
	<attribute name="Time Scale" value="1" />
	<attribute name="Smoothing Constant" value="50" />
	<attribute name="Snap Threshold" value="5" />
	<attribute name="Elapsed Time" value="0" />
	<attribute name="Next Replicated Node ID" value="1000" />
	<attribute name="Next Replicated Component ID" value="1000" />
	<attribute name="Next Local Node ID" value="16777216" />
	<attribute name="Next Local Component ID" value="16777216" />
	<attribute name="Variables" />
	<attribute name="Variable Names" value="" />
{scene_environment()}	<node id="{root_id}">
		<attribute name="Is Enabled" value="true" />
		<attribute name="Name" value="LibraryObject" />
		<attribute name="Tags" />
		<attribute name="Position" value="0 0 0" />
		<attribute name="Rotation" value="{quat_identity()}" />
		<attribute name="Scale" value="1 1 1" />
		<attribute name="Variables" />
{object_nodes}	</node>
</scene>
"""


def primitive(name: str, model: str, material: str,
              pos: Tuple[float, float, float],
              scale: Tuple[float, float, float]) -> str:
    n = nid()
    return (
        node_open(n, name, pos, scale)
        + static_model(model, material)
        + node_close()
    )


def build_object_scene(scene_title: str, parts: Iterable[str]) -> str:
    reset_ids()
    body = "".join(parts)
    return wrap_scene(scene_title, body)


def pack_mur_scene(out_path: Path, xml_name: str, xml_body: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    config = json.dumps({"version": 1.0}, indent=4)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("Config.json", config)
        zf.writestr(xml_name, xml_body)


M = "Materials/Objects/Colors"
BOX = "Models/Box.mdl"
SPHERE = "Models/Sphere.mdl"
CYL = "Models/Cylinder.mdl"
CONE = "Models/Cone.mdl"
PLANE = "Models/Plane.mdl"


def define_objects() -> List[Tuple[str, Path, str]]:
    """(filename, folder, xml)"""
    items: List[Tuple[str, Path, str]] = []

    def add(folder: str, fname: str, xml: str) -> None:
        items.append((fname, ROOT / folder, xml))

    # --- Markers ---
    add("Markers", "marker_start_red",
        build_object_scene("marker_start_red", [
            primitive("StartMarker", BOX, f"{M}/Red.xml", (0, -1.5, 0), (0.5, 0.5, 0.5)),
        ]))

    add("Markers", "marker_finish_green",
        build_object_scene("marker_finish_green", [
            primitive("FinishMarker", SPHERE, f"{M}/Green.xml", (0, -1.5, 0), (0.5, 0.5, 0.5)),
        ]))

    for color, mat, fname in [
        ("Yellow", "Yellow", "marker_waypoint_yellow"),
        ("Blue", "Blue", "marker_waypoint_blue"),
        ("Orange", "Orange", "marker_waypoint_orange"),
        ("Purple", "Magenta", "marker_waypoint_purple"),
    ]:
        add("Markers", fname, build_object_scene(fname, [
            primitive("Waypoint", CYL, f"{M}/{mat}.xml", (0, -1.5, 0), (0.35, 0.5, 0.35)),
        ]))

    arrow = (
        primitive("ArrowBase", BOX, f"{M}/Yellow.xml", (0, -1.5, 0), (1.0, 0.2, 0.1))
        + primitive("ArrowTip", BOX, f"{M}/Yellow.xml", (0.7, -1.5, 0), (0.4, 0.4, 0.1))
    )
    add("Markers", "marker_direction_arrow", build_object_scene("marker_direction_arrow", [arrow]))

    depth = (
        primitive("Pole", CYL, f"{M}/Cyan.xml", (0, -0.5, 0), (0.08, 2.0, 0.08))
        + primitive("Ring1", BOX, f"{M}/Red.xml", (0.35, 0.2, 0), (0.4, 0.05, 0.05))
        + primitive("Ring2", BOX, f"{M}/Yellow.xml", (0.35, -0.5, 0), (0.4, 0.05, 0.05))
        + primitive("Ring3", BOX, f"{M}/Green.xml", (0.35, -1.2, 0), (0.4, 0.05, 0.05))
    )
    add("Markers", "marker_depth_pole", build_object_scene("marker_depth_pole", [depth]))

    # --- Obstacles ---
    add("Obstacles", "obstacle_pole_red",
        build_object_scene("obstacle_pole_red", [
            primitive("Pole", CYL, f"{M}/Red.xml", (0, 0, 0), (0.2, 2.5, 0.2)),
        ]))

    add("Obstacles", "obstacle_beam_horizontal",
        build_object_scene("obstacle_beam_horizontal", [
            primitive("Beam", BOX, f"{M}/Orange.xml", (0, -1.0, 0), (3.0, 0.25, 0.25)),
        ]))

    gate = (
        primitive("PostLeft", CYL, f"{M}/Red.xml", (-1.25, 0, 0), (0.2, 2.0, 0.2))
        + primitive("PostRight", CYL, f"{M}/Red.xml", (1.25, 0, 0), (0.2, 2.0, 0.2))
        + primitive("Crossbar", BOX, f"{M}/Red.xml", (0, 1.0, 0), (2.5, 0.15, 0.15))
    )
    add("Obstacles", "obstacle_gate", build_object_scene("obstacle_gate", [gate]))

    corner = (
        primitive("LegX", BOX, f"{M}/Red.xml", (0, -1.0, 0), (2.0, 0.2, 0.2))
        + primitive("LegZ", BOX, f"{M}/Red.xml", (0.9, -1.0, 0.9), (0.2, 0.2, 2.0))
    )
    add("Obstacles", "obstacle_corner_L", build_object_scene("obstacle_corner_L", [corner]))

    maze = ""
    for i, (x, z, ry) in enumerate([(0, 0, 0), (2, 1, 25), (-2, 2, -20), (1, -2, 40)]):
        maze += primitive(f"Wall{i}", BOX, f"{M}/Black.xml", (x, 0, z), (0.15, 1.8, 1.2))
    add("Obstacles", "obstacle_maze_walls", build_object_scene("obstacle_maze_walls", [maze]))

    # --- Navigation ---
    add("Navigation", "nav_track_line_white",
        build_object_scene("nav_track_line_white", [
            primitive("TrackLine", BOX, "Materials/Objects/Generic.xml", (0, -1.8, 0), (6.0, 0.03, 0.15)),
        ]))

    add("Navigation", "nav_zone_start",
        build_object_scene("nav_zone_start", [
            primitive("StartZone", PLANE, f"{M}/Green.xml", (0, -1.85, 0), (2.0, 1.0, 2.0)),
        ]))

    add("Navigation", "nav_zone_finish",
        build_object_scene("nav_zone_finish", [
            primitive("FinishZone", PLANE, f"{M}/Red.xml", (0, -1.85, 0), (2.0, 1.0, 2.0)),
        ]))

    digit1 = primitive("DigitStem", BOX, f"{M}/Yellow.xml", (0, -1.2, 0), (0.1, 1.0, 0.1))
    add("Navigation", "nav_digit_1", build_object_scene("nav_digit_1", [digit1]))

    buoy = (
        primitive("Stem", CYL, f"{M}/Black.xml", (0, -1.6, 0), (0.05, 0.8, 0.05))
        + primitive("Float", SPHERE, f"{M}/Cyan.xml", (0, -1.0, 0), (0.35, 0.35, 0.35))
    )
    add("Navigation", "nav_buoy", build_object_scene("nav_buoy", [buoy]))

    # --- Terrain ---
    add("Terrain", "terrain_rock_gray",
        build_object_scene("terrain_rock_gray", [
            primitive("Rock", SPHERE, f"{M}/Black.xml", (0, -1.7, 0), (0.8, 0.5, 0.7)),
        ]))

    add("Terrain", "terrain_plant_cone",
        build_object_scene("terrain_plant_cone", [
            primitive("Plant", CONE, f"{M}/Green.xml", (0, -1.5, 0), (0.4, 0.8, 0.4)),
        ]))

    add("Terrain", "terrain_pipe_straight",
        build_object_scene("terrain_pipe_straight", [
            primitive("Pipe", CYL, f"{M}/Orange.xml", (0, -1.5, 0), (0.15, 0.15, 3.0)),
        ]))

    # --- Composite objects ---
    pier = (
        primitive("Pillar1", BOX, f"{M}/Black.xml", (-0.8, -1.2, 0), (0.4, 1.5, 0.4))
        + primitive("Pillar2", BOX, f"{M}/Black.xml", (0.8, -1.2, 0), (0.4, 1.5, 0.4))
        + primitive("Deck", BOX, f"{M}/Black.xml", (0, -0.3, 0), (2.2, 0.2, 1.0))
    )
    add("Composite", "composite_bridge_pier", build_object_scene("composite_bridge_pier", [pier]))

    wreck = (
        primitive("Hull", BOX, f"{M}/Orange.xml", (0, -1.5, 0), (1.2, 0.6, 0.8))
        + primitive("PipeA", CYL, f"{M}/Black.xml", (0.5, -1.2, 0), (0.15, 0.15, 0.8))
        + primitive("PipeB", CYL, f"{M}/Black.xml", (-0.4, -1.3, 0.3), (0.12, 0.12, 0.6))
    )
    add("Composite", "composite_wreck_simple", build_object_scene("composite_wreck_simple", [wreck]))

    return items


def build_example_scenes() -> List[Tuple[str, Path, str]]:
    """Учебные полигоны из нескольких объектов (раздел 3.5 ТЗ)."""
    examples: List[Tuple[str, Path, str]] = []

    def example(name: str, parts: Iterable[str]) -> None:
        examples.append((name, ROOT / "Examples", build_object_scene(name, parts)))

    course = (
        primitive("Start", BOX, f"{M}/Red.xml", (-4, -1.5, 0), (0.5, 0.5, 0.5))
        + primitive("W1", CYL, f"{M}/Yellow.xml", (-2, -1.5, 0), (0.35, 0.5, 0.35))
        + primitive("W2", CYL, f"{M}/Blue.xml", (0, -1.5, 0), (0.35, 0.5, 0.35))
        + primitive("W3", CYL, f"{M}/Orange.xml", (2, -1.5, 0), (0.35, 0.5, 0.35))
        + primitive("Finish", SPHERE, f"{M}/Green.xml", (4, -1.5, 0), (0.5, 0.5, 0.5))
        + primitive("Track", BOX, "Materials/Objects/Generic.xml", (0, -1.85, 0), (10.0, 0.03, 0.2))
    )
    example("example_markers_course", course)

    lane = (
        primitive("Pole", CYL, f"{M}/Red.xml", (-2, 0, -2), (0.2, 2.5, 0.2))
        + primitive("Beam", BOX, f"{M}/Orange.xml", (0, -0.5, 0), (3.0, 0.25, 0.25))
        + primitive("GateL", CYL, f"{M}/Red.xml", (2, 0, 2), (0.2, 2.0, 0.2))
        + primitive("GateR", CYL, f"{M}/Red.xml", (4, 0, 2), (0.2, 2.0, 0.2))
        + primitive("GateBar", BOX, f"{M}/Red.xml", (3, 1.0, 2), (2.5, 0.15, 0.15))
    )
    example("example_obstacle_lane", lane)

    nav = (
        primitive("LineA", BOX, "Materials/Objects/Generic.xml", (0, -1.85, -3), (8.0, 0.03, 0.15))
        + primitive("LineB", BOX, "Materials/Objects/Generic.xml", (0, -1.85, 3), (8.0, 0.03, 0.15))
        + primitive("ZoneS", PLANE, f"{M}/Green.xml", (-3, -1.85, 0), (1.5, 1.0, 1.5))
        + primitive("ZoneF", PLANE, f"{M}/Red.xml", (3, -1.85, 0), (1.5, 1.0, 1.5))
        + primitive("Buoy1", SPHERE, f"{M}/Cyan.xml", (0, -1.2, 0), (0.4, 0.4, 0.4))
    )
    example("example_navigation_track", nav)

    return examples


def main() -> None:
    all_items = define_objects() + build_example_scenes()
    for fname, folder, xml in all_items:
        xml_file = f"{fname}.xml"
        out = folder / f"{fname}.mur_scene"
        pack_mur_scene(out, xml_file, xml)
        print(f"  {out.relative_to(ROOT)}")

    print(f"\nГотово: {len(all_items)} сцен в {ROOT}")


if __name__ == "__main__":
    main()
