import pytest

from app.data import generate_amounts, load_amounts_from_csv


def test_generate_is_reproducible():
    assert generate_amounts(50, seed=1) == generate_amounts(50, seed=1)


def test_generate_changes_with_seed():
    assert generate_amounts(50, seed=1) != generate_amounts(50, seed=2)


def test_generate_values_are_positive():
    assert all(a > 0 for a in generate_amounts(200))


def test_generate_rejects_bad_n():
    with pytest.raises(ValueError):
        generate_amounts(0)


def test_load_csv_reads_valid_rows(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("id,amount\n1,10.5\n2,abc\n3,-4\n4,20\n", encoding="utf-8")
    assert load_amounts_from_csv(path) == [10.5, 20.0]


def test_load_csv_missing_column(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("id,value\n1,5\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_amounts_from_csv(path)


def test_load_csv_without_valid_rows(tmp_path):
    path = tmp_path / "t.csv"
    path.write_text("id,amount\n1,abc\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_amounts_from_csv(path)
