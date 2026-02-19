def move_pointer(scene, pointers, pointer_index, new_position, alignment):
    scene.play(pointers[pointer_index].animate.move_to(new_position, aligned_edge=alignment))
