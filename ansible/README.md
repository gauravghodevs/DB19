# Ansible Operations

## Inventory

`inventory/localhost.ini` targets localhost only. Replace it with a reviewed
inventory before targeting remote infrastructure.

## Read-only audit

After installing Ansible in a dedicated environment, run:

```bash
ansible-playbook \
  -i ansible/inventory/localhost.ini \
  ansible/playbooks/audit.yml \
  --syntax-check

ansible-playbook \
  -i ansible/inventory/localhost.ini \
  ansible/playbooks/audit.yml
```

The audit gathers operating-system facts and reads root filesystem usage. It
does not install packages or change system configuration.

Review and test any future hardening playbook on disposable lab hosts before
applying it to production systems.
