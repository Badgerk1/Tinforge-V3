import hashlib

from tinforge.tp3.object_relationships import (
    EXPECTED_FILE_SHA256,
    SURFACE_NAME_UTF16LE,
    analyze_stage5_object_relationships,
    enforce_golden_reference_identity,
)


def test_stage5_object_relationships_require_original_golden_identity(
    original_professional_tp3_bytes: bytes,
):
    assert hashlib.sha256(original_professional_tp3_bytes).hexdigest() == EXPECTED_FILE_SHA256
    enforce_golden_reference_identity(original_professional_tp3_bytes)


def test_stage5_surface_metadata_links_to_geometry_counts(
    original_professional_tp3_bytes: bytes,
):
    evidence = analyze_stage5_object_relationships(original_professional_tp3_bytes)
    assert evidence.type14_payload_matches_verified_triangle_range
    assert evidence.type14_payload_matches_verified_triangle_bytes
    assert evidence.type17_metadata.vertex_count == 53
    assert evidence.type17_metadata.triangle_count == 76
    assert evidence.type17_metadata.surface_name == SURFACE_NAME_UTF16LE
    assert evidence.type17_metadata.origin_candidate_x == 295399.97869873
    assert evidence.type17_metadata.origin_candidate_y == 4843987.442024235
    assert evidence.type17_metadata.origin_candidate_x_relative_offset == 160
    assert evidence.type17_metadata.origin_candidate_y_relative_offset == 168


def test_stage5_non_sentinel_link_fields_are_in_bounds_and_cross_region_candidates(
    original_professional_tp3_bytes: bytes,
):
    evidence = analyze_stage5_object_relationships(original_professional_tp3_bytes)
    observed = {
        (reference.container_type, reference.field_name, reference.value): reference
        for reference in evidence.link_references
    }
    assert set(observed) == {
        (2, "link_next", 350324),
        (13, "link_next", 349794),
    }
    for reference in observed.values():
        assert reference.is_in_bounds
        assert reference.points_before_surface_region
        assert not reference.matches_container_header_offset


def test_stage5_finding_classifications_cover_required_labels(
    original_professional_tp3_bytes: bytes,
):
    evidence = analyze_stage5_object_relationships(original_professional_tp3_bytes)
    by_subject = {finding.subject: finding for finding in evidence.findings}
    assert by_subject["18-byte container header size"].classification == "VERIFIED"
    assert by_subject["type-14 triangle payload anchor"].classification == "VERIFIED"
    assert (
        by_subject["surface metadata to vertex geometry linkage"].classification
        == "SUPPORTED HYPOTHESIS"
    )
    assert (
        by_subject["surface metadata to triangle geometry linkage"].classification
        == "SUPPORTED HYPOTHESIS"
    )
    assert (
        by_subject["container link fields as cross-region object references"].classification
        == "SUPPORTED HYPOTHESIS"
    )
    assert (
        by_subject["candidate origin/localization doubles in type-17"].classification
        == "SUPPORTED HYPOTHESIS"
    )
    assert (
        by_subject["semantic meaning of container field_2 and link directionality"].classification
        == "UNKNOWN"
    )
    assert (
        by_subject["type-17 name location outside container payload"].classification
        == "REJECTED HYPOTHESIS"
    )
    assert "431906:433730" in by_subject["type-14 triangle payload anchor"].evidence
    assert (
        "no explicit type-17 pointer/reference"
        in by_subject["surface metadata to vertex geometry linkage"].evidence
    )
    assert (
        "no explicit type-17 pointer/reference"
        in by_subject["surface metadata to triangle geometry linkage"].evidence
    )
    assert "vertex_count@+18" in by_subject["type-17 surface metadata payload anchors"].evidence
    assert "triangle_count@+22" in by_subject["type-17 surface metadata payload anchors"].evidence
    assert "name@+30='design grade'" in by_subject["type-17 surface metadata payload anchors"].evidence
    assert evidence.type17_metadata.payload_offset == 433748
    assert evidence.type17_metadata.payload_size == 332
    assert evidence.type17_metadata.vertex_count_relative_offset == 18
    assert evidence.type17_metadata.triangle_count_relative_offset == 22
    assert evidence.type17_metadata.surface_name_relative_offset == 30
    assert evidence.type17_metadata.origin_candidate_x_relative_offset == 160
    assert evidence.type17_metadata.origin_candidate_y_relative_offset == 168
