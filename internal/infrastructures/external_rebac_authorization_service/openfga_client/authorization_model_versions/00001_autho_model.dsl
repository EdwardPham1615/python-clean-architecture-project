model
  schema 1.1

type user
  relations
    define can_create: [user] or is_super_admin or is_owner
    define can_delete: [user] or is_super_admin or is_owner
    define can_get_detail: [user] or is_super_admin or is_owner
    define can_get_list: [user] or is_super_admin or is_owner
    define can_update: [user] or is_super_admin or is_owner
    define is_super_admin: [user]
    define is_owner: [user]

type post
  relations
    define can_delete: [user, user#is_super_admin] or is_owner
    define can_update: [user, user#is_super_admin] or is_owner
    define is_owner: [user]

type comment
  relations
    define can_delete: [user, user#is_super_admin] or is_owner
    define can_update: [user, user#is_super_admin] or is_owner
    define is_owner: [user]
