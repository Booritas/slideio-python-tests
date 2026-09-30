"""slideio PHTIFF driver testing.

Philips whole-slide TIFFs are read by the PHTIFF driver, not by a driver named
after the vendor: open_slide(path, "PHILIPS") fails.  The four corpus files
differ in pyramid depth and in which auxiliary images the scanner wrote, which
is what makes them worth testing as a set rather than one representative.
"""
import numpy as np
import pytest
import slideio

from common.test_tools import image_path

# subpath -> size, magnification, resolution (x, y), zoom levels, aux names
SLIDES = {
    "Philips-1.tiff": ((45056, 35840), 44.0, (2.268910e-07, 2.269070e-07), 8, []),
    "Philips-2.tiff": ((97280, 217600), 41.0, (2.430940e-07, 2.430940e-07), 10, ["Macro"]),
    "Philips-3.tiff": ((131072, 100352), 44.0, (2.268910e-07, 2.269070e-07), 9,
                       ["Label", "Macro"]),
    "Philips-4.tiff": ((91136, 68096), 40.0, (2.500000e-07, 2.500000e-07), 9, ["Macro"]),
}


@pytest.fixture
def phtiff_slide(opened_slide):
    def _open(subpath):
        return opened_slide(image_path("philips", subpath), "PHTIFF")
    return _open


class TestDriverRegistration:

    def test_driver_is_registered(self):
        assert "PHTIFF" in slideio.get_driver_ids()

    def test_vendor_name_is_not_a_driver_id(self):
        """The driver is PHTIFF; "PHILIPS" is not an alias for it."""
        assert "PHILIPS" not in slideio.get_driver_ids()
        with pytest.raises(RuntimeError):
            slideio.open_slide(image_path("philips", "Philips-1.tiff"), "PHILIPS")

    def test_not_existing_file(self):
        with pytest.raises(RuntimeError):
            slideio.open_slide("missing_file.tiff", "PHTIFF")


class TestPhilipsSlides:

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_single_scene(self, subpath, phtiff_slide):
        assert phtiff_slide(subpath).num_scenes == 1

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_scene_geometry(self, subpath, phtiff_slide):
        size, magnification, resolution, zoom_levels, _ = SLIDES[subpath]
        scene = phtiff_slide(subpath).get_scene(0)
        assert scene.size == size
        assert scene.rect == (0, 0) + size
        assert scene.magnification == magnification
        assert scene.num_zoom_levels == zoom_levels
        assert scene.resolution[0] == pytest.approx(resolution[0], rel=1e-5)
        assert scene.resolution[1] == pytest.approx(resolution[1], rel=1e-5)

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_scene_is_8_bit_rgb(self, subpath, phtiff_slide):
        scene = phtiff_slide(subpath).get_scene(0)
        assert scene.num_channels == 3
        assert scene.get_channel_data_type(0) == np.uint8
        assert scene.compression == slideio.Compression.Jpeg

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_metadata_is_xml(self, subpath, phtiff_slide):
        # Compared by name: the MetadataFormat enum is not exported from the
        # slideio package, so there is no public constant to compare against.
        # See core/test_public_api.py.
        assert phtiff_slide(subpath).metadata_format.name == "XML"

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_auxiliary_images(self, subpath, phtiff_slide):
        """Aux images hang off the slide, not the scene, for this format."""
        _, _, _, _, aux_names = SLIDES[subpath]
        slide = phtiff_slide(subpath)
        assert slide.num_aux_images == len(aux_names)
        assert sorted(slide.get_aux_image_names()) == sorted(aux_names)
        assert slide.get_scene(0).num_aux_images == 0

    @pytest.mark.parametrize("subpath",
                             sorted(k for k, v in SLIDES.items() if v[4]))
    def test_auxiliary_image_raster(self, subpath, phtiff_slide):
        slide = phtiff_slide(subpath)
        for name in SLIDES[subpath][4]:
            raster = slide.get_aux_image_raster(name)
            assert raster.ndim == 3
            assert raster.shape[2] == 3
            assert raster.size > 0

    @pytest.mark.parametrize("subpath", sorted(SLIDES))
    def test_block_read_from_top_pyramid_level(self, subpath, phtiff_slide):
        """The smallest level, so the read stays cheap on 100k-pixel slides."""
        scene = phtiff_slide(subpath).get_scene(0)
        top = scene.num_zoom_levels - 1
        info = scene.get_zoom_level_info(top)
        raster = scene.read_block_from_level(top, rect=(0, 0, 128, 128))
        assert raster.shape == (128, 128, 3)
        assert info.size.width < scene.size[0]
