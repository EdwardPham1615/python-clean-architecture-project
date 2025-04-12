model
schema 1.1

type user
    relations
        define is_super_admin: [user]
        define can_create: [user] or is_super_admin
        define can_get_detail: [user] or is_super_admin
        define can_get_list: [user] or is_super_admin
        define can_update: [user] or is_super_admin
        define can_delete: [user] or is_super_admin

type post
    relations
        define is_owner: [user]
        define can_update: [user, user#is_super_admin] or is_owner
        define can_delete: [user, user#is_super_admin] or is_owner

type comment
    relations
        define is_owner: [user]
        define can_update: [user, user#is_super_admin] or is_owner
        define can_delete: [user, user#is_super_admin] or is_owner
