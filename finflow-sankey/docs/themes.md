# Themes & Palettes

## Built-in Themes

- `default`
- `monochrome`
- `colorblind_safe`
- `minimal`
- `dark`

```python
fig = FinancialSankey.income_statement(df).validate().render(theme="dark")
```

## Custom Palette via YAML

```yaml
name: "my_theme"
roles:
  revenue: "#0055FF"
  operating_expenses: "#CC0000"
  profit: "#00AA55"
semantic:
  background: "#FFFFFF"
  link_opacity: 0.45
```

```python
fig = FinancialSankey.income_statement(df).validate().render(palette="my_theme.yaml")
```

## Runtime Dict Override

```python
fig = FinancialSankey.income_statement(df).validate().render(
    palette={"revenue": "#FF0000", "profit": "#00FF00"}
)
```
