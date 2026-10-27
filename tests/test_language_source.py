from backend.language_sources.voix_du_togo import audit


def test_refuses_non_official_host_without_network():
    result = audit("https://example.com/not-voix-du-togo")
    assert result["status"] == "refused"
    assert result["resource_links"] == []
