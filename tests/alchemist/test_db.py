# -*- coding: utf-8 -*-
import sys
import pytest
from alchemist.db import models


class BaseTest:

    def setup(self):
        # Unload all alchemist.* modules and test packages.
        for name in list(sys.modules.keys()):
            for test in ['a', 'a.b', 'a.b.c', 'example', 'alchemist']:
                if name.startswith(test) and name in sys.modules:
                    del sys.modules[name]


class TestModels(BaseTest):

    def test_package_resolution_nested_no_context(self):
        assert models._package_of('a.models') == 'a'
        assert models._package_of('a.b.models') == 'a.b'
        assert models._package_of('a.b') == 'a.b'
        assert models._package_of('a.b.c.models') == 'a.b.c'
        assert models._package_of('a.b.c.models.models') == 'a.b.c'

    def test_package_resolution_simple_no_context(self):
        assert models._package_of('example.models') == 'example'

    def test_package_resolution_nested_with_context(self):
        from a import application
        with application.app_context():
            assert models._package_of('a.models') == 'a'
            assert models._package_of('a.b.models') == 'a.b'
            assert models._package_of('a.b.c.models') == 'a.b'

    def test_package_resolution_simple_with_context(self):
        from example import application
        with application.app_context():
            assert models._package_of('example.models') == 'example'

    @staticmethod
    def _get_registry(obj):
        return obj._decl_class_registry.values()

    @staticmethod
    def _tables(obj):
        return obj.metadata.tables.values()

    def test_class_registry_nested_no_context(self):
        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert c.CBlock not in self._get_registry(b.BBlock)
        assert c.CBlock not in self._get_registry(b.BWall)
        assert c.CBlock not in self._get_registry(a.ABlock)
        assert c.CBlock not in self._get_registry(a.AWall)
        assert c.CBlock in self._get_registry(c.CBlock)
        assert c.CBlock in self._get_registry(c.CWall)

        assert b.BBlock not in self._get_registry(c.CBlock)
        assert b.BBlock not in self._get_registry(c.CWall)
        assert b.BBlock not in self._get_registry(a.ABlock)
        assert b.BBlock not in self._get_registry(a.AWall)
        assert b.BBlock in self._get_registry(b.BBlock)
        assert b.BBlock in self._get_registry(b.BWall)

        assert a.ABlock not in self._get_registry(b.BBlock)
        assert a.ABlock not in self._get_registry(b.BWall)
        assert a.ABlock not in self._get_registry(c.CBlock)
        assert a.ABlock not in self._get_registry(c.CWall)
        assert a.ABlock in self._get_registry(a.ABlock)
        assert a.ABlock in self._get_registry(a.AWall)

        assert c.CWall not in self._get_registry(b.BBlock)
        assert c.CWall not in self._get_registry(b.BWall)
        assert c.CWall not in self._get_registry(a.ABlock)
        assert c.CWall not in self._get_registry(a.AWall)
        assert c.CWall in self._get_registry(c.CBlock)
        assert c.CWall in self._get_registry(c.CWall)

        assert b.BWall not in self._get_registry(c.CBlock)
        assert b.BWall not in self._get_registry(c.CWall)
        assert b.BWall not in self._get_registry(a.ABlock)
        assert b.BWall not in self._get_registry(a.AWall)
        assert b.BWall in self._get_registry(b.BBlock)
        assert b.BWall in self._get_registry(b.BWall)

        assert a.AWall not in self._get_registry(b.BBlock)
        assert a.AWall not in self._get_registry(b.BWall)
        assert a.AWall not in self._get_registry(c.CBlock)
        assert a.AWall not in self._get_registry(c.CWall)
        assert a.AWall in self._get_registry(a.ABlock)
        assert a.AWall in self._get_registry(a.AWall)

    def test_class_registry_simple_no_context(self):
        from example import models

        assert models.ExampleWall in self._get_registry(models.ExampleWall)
        assert models.ExampleBlock in self._get_registry(models.ExampleBlock)

    def test_tables_nested_no_context(self):
        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert c.CBlock.__table__ not in self._tables(b.BBlock)
        assert c.CBlock.__table__ not in self._tables(b.BWall)
        assert c.CBlock.__table__ not in self._tables(a.ABlock)
        assert c.CBlock.__table__ not in self._tables(a.AWall)
        assert c.CBlock.__table__ in self._tables(c.CBlock)
        assert c.CBlock.__table__ in self._tables(c.CWall)

        assert b.BBlock.__table__ not in self._tables(c.CBlock)
        assert b.BBlock.__table__ not in self._tables(c.CWall)
        assert b.BBlock.__table__ not in self._tables(a.ABlock)
        assert b.BBlock.__table__ not in self._tables(a.AWall)
        assert b.BBlock.__table__ in self._tables(b.BBlock)
        assert b.BBlock.__table__ in self._tables(b.BWall)

        assert a.ABlock.__table__ not in self._tables(b.BBlock)
        assert a.ABlock.__table__ not in self._tables(b.BWall)
        assert a.ABlock.__table__ not in self._tables(c.CBlock)
        assert a.ABlock.__table__ not in self._tables(c.CWall)
        assert a.ABlock.__table__ in self._tables(a.ABlock)
        assert a.ABlock.__table__ in self._tables(a.AWall)

        assert c.CWall.__table__ not in self._tables(b.BBlock)
        assert c.CWall.__table__ not in self._tables(b.BWall)
        assert c.CWall.__table__ not in self._tables(a.ABlock)
        assert c.CWall.__table__ not in self._tables(a.AWall)
        assert c.CWall.__table__ in self._tables(c.CBlock)
        assert c.CWall.__table__ in self._tables(c.CWall)

        assert b.BWall.__table__ not in self._tables(c.CBlock)
        assert b.BWall.__table__ not in self._tables(c.CWall)
        assert b.BWall.__table__ not in self._tables(a.ABlock)
        assert b.BWall.__table__ not in self._tables(a.AWall)
        assert b.BWall.__table__ in self._tables(b.BBlock)
        assert b.BWall.__table__ in self._tables(b.BWall)

        assert a.AWall.__table__ not in self._tables(b.BBlock)
        assert a.AWall.__table__ not in self._tables(b.BWall)
        assert a.AWall.__table__ not in self._tables(c.CBlock)
        assert a.AWall.__table__ not in self._tables(c.CWall)
        assert a.AWall.__table__ in self._tables(a.ABlock)
        assert a.AWall.__table__ in self._tables(a.AWall)

    def test_tables_simple_no_context(self):
        from example import models as e

        assert e.ExampleWall.__table__ in self._tables(e.ExampleWall)
        assert e.ExampleBlock.__table__ in self._tables(e.ExampleBlock)

    def test_class_registry_nested_with_context(self):
        from a import application

        context = application.app_context()
        context.push()

        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert c.CBlock in self._get_registry(b.BBlock)
        assert c.CBlock in self._get_registry(b.BWall)
        assert c.CBlock not in self._get_registry(a.ABlock)
        assert c.CBlock not in self._get_registry(a.AWall)
        assert c.CBlock in self._get_registry(c.CBlock)
        assert c.CBlock in self._get_registry(c.CWall)

        assert b.BBlock in self._get_registry(c.CBlock)
        assert b.BBlock in self._get_registry(c.CWall)
        assert b.BBlock not in self._get_registry(a.ABlock)
        assert b.BBlock not in self._get_registry(a.AWall)
        assert b.BBlock in self._get_registry(b.BBlock)
        assert b.BBlock in self._get_registry(b.BWall)

        assert a.ABlock not in self._get_registry(b.BBlock)
        assert a.ABlock not in self._get_registry(b.BWall)
        assert a.ABlock not in self._get_registry(c.CBlock)
        assert a.ABlock not in self._get_registry(c.CWall)
        assert a.ABlock in self._get_registry(a.ABlock)
        assert a.ABlock in self._get_registry(a.AWall)

        assert c.CWall in self._get_registry(b.BBlock)
        assert c.CWall in self._get_registry(b.BWall)
        assert c.CWall not in self._get_registry(a.ABlock)
        assert c.CWall not in self._get_registry(a.AWall)
        assert c.CWall in self._get_registry(c.CBlock)
        assert c.CWall in self._get_registry(c.CWall)

        assert b.BWall in self._get_registry(c.CBlock)
        assert b.BWall in self._get_registry(c.CWall)
        assert b.BWall not in self._get_registry(a.ABlock)
        assert b.BWall not in self._get_registry(a.AWall)
        assert b.BWall in self._get_registry(b.BBlock)
        assert b.BWall in self._get_registry(b.BWall)

        assert a.AWall not in self._get_registry(b.BBlock)
        assert a.AWall not in self._get_registry(b.BWall)
        assert a.AWall not in self._get_registry(c.CBlock)
        assert a.AWall not in self._get_registry(c.CWall)
        assert a.AWall in self._get_registry(a.ABlock)
        assert a.AWall in self._get_registry(a.AWall)

        context.pop()

    def test_class_registry_simple_with_context(self):
        from example import application

        context = application.app_context()
        context.push()

        from example import models

        assert models.ExampleWall in self._get_registry(models.ExampleWall)
        assert models.ExampleBlock in self._get_registry(models.ExampleBlock)

        context.pop()

    def test_tables_nested_with_context(self):
        from a import application

        context = application.app_context()
        context.push()

        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert c.CBlock.__table__ in self._tables(b.BBlock)
        assert c.CBlock.__table__ in self._tables(b.BWall)
        assert c.CBlock.__table__ not in self._tables(a.ABlock)
        assert c.CBlock.__table__ not in self._tables(a.AWall)
        assert c.CBlock.__table__ in self._tables(c.CBlock)
        assert c.CBlock.__table__ in self._tables(c.CWall)

        assert b.BBlock.__table__ in self._tables(c.CBlock)
        assert b.BBlock.__table__ in self._tables(c.CWall)
        assert b.BBlock.__table__ not in self._tables(a.ABlock)
        assert b.BBlock.__table__ not in self._tables(a.AWall)
        assert b.BBlock.__table__ in self._tables(b.BBlock)
        assert b.BBlock.__table__ in self._tables(b.BWall)

        assert a.ABlock.__table__ not in self._tables(b.BBlock)
        assert a.ABlock.__table__ not in self._tables(b.BWall)
        assert a.ABlock.__table__ not in self._tables(c.CBlock)
        assert a.ABlock.__table__ not in self._tables(c.CWall)
        assert a.ABlock.__table__ in self._tables(a.ABlock)
        assert a.ABlock.__table__ in self._tables(a.AWall)

        assert c.CWall.__table__ in self._tables(b.BBlock)
        assert c.CWall.__table__ in self._tables(b.BWall)
        assert c.CWall.__table__ not in self._tables(a.ABlock)
        assert c.CWall.__table__ not in self._tables(a.AWall)
        assert c.CWall.__table__ in self._tables(c.CBlock)
        assert c.CWall.__table__ in self._tables(c.CWall)

        assert b.BWall.__table__ in self._tables(c.CBlock)
        assert b.BWall.__table__ in self._tables(c.CWall)
        assert b.BWall.__table__ not in self._tables(a.ABlock)
        assert b.BWall.__table__ not in self._tables(a.AWall)
        assert b.BWall.__table__ in self._tables(b.BBlock)
        assert b.BWall.__table__ in self._tables(b.BWall)

        assert a.AWall.__table__ not in self._tables(b.BBlock)
        assert a.AWall.__table__ not in self._tables(b.BWall)
        assert a.AWall.__table__ not in self._tables(c.CBlock)
        assert a.AWall.__table__ not in self._tables(c.CWall)
        assert a.AWall.__table__ in self._tables(a.ABlock)
        assert a.AWall.__table__ in self._tables(a.AWall)

        context.pop()

    def test_tables_simple_with_context(self):
        from example import application

        context = application.app_context()
        context.push()

        from example import models as e

        assert e.ExampleWall.__table__ in self._tables(e.ExampleWall)
        assert e.ExampleBlock.__table__ in self._tables(e.ExampleBlock)

        context.pop()

    def test_table_name_nested_no_context(self):
        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert a.ABlock.__table__.name == 'a_ablock'
        assert b.BWall.__table__.name == 'a_b_bwall'
        assert c.CWall.__table__.name == 'a_b_c_cwall'

    def test_table_name_simple_no_context(self):
        from example import models

        assert models.ExampleWall.__table__.name == 'example_examplewall'

    def test_table_name_nested_with_context(self):
        from a import application

        context = application.app_context()
        context.push()

        from a import models as a
        from a.b import models as b
        from a.b.c import models as c

        assert a.ABlock.__table__.name == 'a_ablock'
        assert b.BWall.__table__.name == 'a_b_bwall'
        assert c.CWall.__table__.name == 'a_b_cwall'

        context.pop()

    def test_table_name_simple_with_context(self):
        from example import application

        context = application.app_context()
        context.push()

        from example import models

        assert models.ExampleWall.__table__.name == 'example_examplewall'

        context.pop()


class TestEngine(BaseTest):

    def test_create(self):
        from a import application as app

        app.metadata['a.b'].create_all(app.databases['default'])


class TestSession(BaseTest):

    def setup(self):
        # Perform base setup.
        super().setup()

        # Ensure all models are created.
        from a import application as app
        app.metadata['a'].create_all(app.databases['default'])
        app.metadata['a.b'].create_all(app.databases['default'])

        # Establish the context.
        self.context = app.app_context()
        self.context.push()

    def teardown(self):
        # Release the context.
        self.context.pop()

    def test_construct(self):
        from alchemist.db import Session

        # Construct a database session.
        session = Session()

        from a.models import AWall

        # Create 2 models.
        session.add(AWall())
        session.add(AWall())

        # Commit.
        session.commit()

        # Query.
        assert len(session.query(AWall).all()) == 2

    def test_scoped_construct(self):
        from alchemist import db
        from a.models import AWall

        # Create 2 models.
        db.session.add(AWall())
        db.session.add(AWall())

        # Commit.
        db.session.commit()

        # Query.
        assert len(db.session.query(AWall).all()) == 2

    def test_save(self):
        from a.models import AWall

        # Create 2 models.
        AWall().save()
        AWall().save(commit=False)

        # Commit.
        from alchemist.db import session
        session.commit()

        # Query.
        assert len(session.query(AWall).all()) == 2

        # Fetch and save.
        m = session.query(AWall).first()
        m.id = 43526
        m.save()

        # Query.
        assert session.query(AWall).filter_by(id=43526).first() is not None

    def test_query(self):
        from a.models import AWall

        # Create 2 models and commit.
        AWall().save()
        AWall().save()

        # Query.
        assert len(AWall.query.all()) == 2

    def test_flail(self):
        from a.models import ABlock

        # Flail.
        with pytest.raises(RuntimeError):
            ABlock.query.flail()
