from projector_controller.config import Size, WindowGeometry
from projector_controller.fit import compute_fit_rect


def test_contain_preserves_source_inside_target() -> None:
    assert compute_fit_rect(Size(400, 200), Size(100, 100), "contain") == WindowGeometry(
        0, 25, 100, 50
    )


def test_cover_preserves_source_and_covers_target() -> None:
    assert compute_fit_rect(Size(400, 200), Size(100, 100), "cover") == WindowGeometry(
        -50, 0, 200, 100
    )


def test_stretch_uses_entire_target() -> None:
    assert compute_fit_rect((400, 200), (100, 100), "stretch") == WindowGeometry(0, 0, 100, 100)


def test_native_centers_source_at_original_size() -> None:
    assert compute_fit_rect((40, 20), (100, 100), "native") == WindowGeometry(30, 40, 40, 20)
