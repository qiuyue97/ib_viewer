# 资金注入记录管理

基础地址：`http://192.168.31.140:8100`

---

## 查询所有记录

```bash
curl http://192.168.31.140:8100/api/capital
```

---

## 新增

```bash
curl -X POST http://192.168.31.140:8100/api/capital \
  -H "Content-Type: application/json" \
  -d '{"amount_cny": 100000.00, "injected_on": "2024-01-15", "note": "初始入金"}'
```

- `amount_cny`：金额，人民币
- `injected_on`：日期，格式 `YYYY-MM-DD`
- `note`：备注，可留空 `""`

---

## 删除

```bash
# 先查询确认 id，再删除
curl -X DELETE http://192.168.31.140:8100/api/capital/1
```

---

## 修改

API 没有 PUT 接口，修改请先删除再重新新增。
