import abc


class AbstractAuthorizationSVC(abc.ABC):
    @abc.abstractmethod
    async def create_perms(self):
        raise NotImplementedError()

    @abc.abstractmethod
    async def delete_perms(self):
        raise NotImplementedError()
